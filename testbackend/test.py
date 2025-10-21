#!/usr/bin/env python

import asyncio
import os
from typing import Optional

import google.generativeai as genai
from google.api_core.exceptions import NotFound
from dotenv import load_dotenv
import websockets


load_dotenv(override=False)


def _configure_model() -> genai.GenerativeModel:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Harap set environment variable GEMINI_API_KEY sebelum menjalankan server.")

    genai.configure(api_key=api_key)
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    return genai.GenerativeModel(model_name)


MODEL = _configure_model()


def _extract_text(response: object) -> Optional[str]:
    text = getattr(response, "text", None)
    if text:
        return text

    for candidate in getattr(response, "candidates", []) or []:
        parts = getattr(getattr(candidate, "content", None), "parts", []) or []
        for part in parts:
            part_text = getattr(part, "text", None)
            if part_text:
                return part_text
    return None


async def generate_response(prompt: str) -> Optional[str]:
    def _call_model() -> Optional[str]:
        try:
            response = MODEL.generate_content(prompt)
        except NotFound as error:
            available_models = [
                model.name
                for model in genai.list_models()
                if "generateContent" in getattr(model, "supported_generation_methods", [])
            ]
            hint = ", ".join(available_models) if available_models else "tidak ada model yang tersedia"
            raise RuntimeError(
                f"Model {getattr(MODEL, 'model_name', 'yang dipilih')} tidak ditemukan. "
                f"Set GEMINI_MODEL ke salah satu model berikut: {hint}"
            ) from error
        return _extract_text(response)

    return await asyncio.to_thread(_call_model)


async def handle_connection(websocket: websockets.WebSocketServerProtocol) -> None:
    try:
        async for incoming in websocket:
            print("Received message:", incoming, flush=True)
            try:
                reply = await generate_response(incoming)
                if not reply:
                    reply = "Maaf, saya tidak menemukan jawaban untuk pertanyaan tersebut."
            except Exception as error:
                print(f"Error while talking to Gemini: {error}", flush=True)
                reply = "Maaf, saya sedang mengalami kendala saat menghubungi layanan AI."

            await websocket.send(reply)
            await websocket.send("[END]")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected", flush=True)
    except Exception as error:
        print(f"Unexpected error: {error}", flush=True)


async def main() -> None:
    print("WebSocket server starting", flush=True)
    port = int(os.environ.get("PORT", 8090))
    async with websockets.serve(
        handle_connection,
        "0.0.0.0",
        port,
    ):
        print(f"WebSocket server running on port {port}", flush=True)
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
