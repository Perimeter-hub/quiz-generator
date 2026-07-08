#!/usr/bin/env python3
"""
Quiz Blitz — YouTube Auto-Uploader
Uploads quiz video (or Short) with metadata from metadata.json:
title, description, tags, category, playlist, scheduled time, thumbnail, pinned comment.

Setup (one time):
  1. Put client_secret.json into shared/ (from Google Cloud Console)
  2. pip3 install google-api-python-client google-auth-oauthlib
  3. First run opens a browser for authorization; token saved to shared/token.json

Usage (from inside a quiz folder):
  python3 ../shared/upload_to_youtube.py            # uploads <folder>_final.mp4
  python3 ../shared/upload_to_youtube.py --short    # uploads <folder>_short.mp4
  python3 ../shared/upload_to_youtube.py --publish-at "2026-07-10T15:00:00-04:00"
"""

import os, sys, json, argparse

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
SHARED_DIR   = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET = os.path.join(SHARED_DIR, "client_secret.json")
TOKEN_PATH    = os.path.join(SHARED_DIR, "token.json")

_folder = os.path.basename(os.path.abspath("."))


def get_service():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        print("Installing Google API libraries...")
        os.system(f"{sys.executable} -m pip install google-api-python-client google-auth-oauthlib -q")
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET):
                print(f"ERROR: {CLIENT_SECRET} not found.")
                print("Download OAuth client JSON from Google Cloud Console and save it there.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def load_metadata(is_short):
    meta_path = "metadata.json"
    if not os.path.exists(meta_path):
        print(f"ERROR: {meta_path} not found in {os.getcwd()}")
        print("Create it (see shared/metadata_template.json) or generate with the quiz.")
        sys.exit(1)
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    key = "short" if is_short else "video"
    if key not in meta:
        print(f"ERROR: '{key}' section missing in metadata.json")
        sys.exit(1)
    return meta[key], meta.get("playlist_id"), meta.get("pinned_comment")


def upload(service, filepath, m, publish_at=None):
    from googleapiclient.http import MediaFileUpload

    body = {
        "snippet": {
            "title":       m["title"],
            "description": m["description"],
            "tags":        m.get("tags", []),
            "categoryId":  m.get("category_id", "24"),   # 24 = Entertainment
            "defaultLanguage": m.get("language", "en"),
            "defaultAudioLanguage": m.get("language", "en"),
        },
        "status": {
            "privacyStatus": "private" if publish_at else m.get("privacy", "public"),
            "selfDeclaredMadeForKids": False,
        },
    }
    if publish_at:
        body["status"]["publishAt"] = publish_at

    print(f"Uploading {filepath} ...")
    media = MediaFileUpload(filepath, chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    video_id = response["id"]
    print(f"  ✅ Uploaded: https://youtube.com/watch?v={video_id}")
    return video_id


def set_thumbnail(service, video_id):
    thumb = os.path.join("images_and_videos", "intro_card.png")
    if not os.path.exists(thumb):
        print("  ℹ  No intro_card.png — skipping thumbnail (first frame will be used)")
        return
    try:
        service.thumbnails().set(videoId=video_id, media_body=thumb).execute()
        print("  ✅ Thumbnail set from intro_card.png")
    except Exception as e:
        print(f"  ⚠  Thumbnail failed (account may need verification): {e}")


def add_to_playlist(service, video_id, playlist_id):
    if not playlist_id:
        return
    try:
        service.playlistItems().insert(
            part="snippet",
            body={"snippet": {"playlistId": playlist_id,
                              "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
        ).execute()
        print(f"  ✅ Added to playlist {playlist_id}")
    except Exception as e:
        print(f"  ⚠  Playlist add failed: {e}")


def pin_comment(service, video_id, text):
    if not text:
        return
    try:
        c = service.commentThreads().insert(
            part="snippet",
            body={"snippet": {"videoId": video_id,
                              "topLevelComment": {"snippet": {"textOriginal": text}}}},
        ).execute()
        print("  ✅ Comment posted (pin it manually in Studio — API can't pin)")
    except Exception as e:
        print(f"  ⚠  Comment failed: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--short", action="store_true", help="upload <folder>_short.mp4")
    ap.add_argument("--publish-at", default=None,
                    help="ISO datetime with timezone, e.g. 2026-07-10T15:00:00-04:00")
    ap.add_argument("--file", default=None, help="override video file path")
    args = ap.parse_args()

    filepath = args.file or (f"{_folder}_short.mp4" if args.short else f"{_folder}_final.mp4")
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} not found. Build it first.")
        sys.exit(1)

    m, playlist_id, pinned = load_metadata(args.short)

    print(f"Quiz Blitz — YouTube Uploader")
    print(f"File:  {filepath}")
    print(f"Title: {m['title']}")
    if args.publish_at:
        print(f"Scheduled: {args.publish_at}")
    print()

    service = get_service()
    video_id = upload(service, filepath, m, args.publish_at)
    if not args.short:
        set_thumbnail(service, video_id)
    add_to_playlist(service, video_id, playlist_id)
    if not args.short:
        pin_comment(service, video_id, pinned)

    print(f"\nDone! Video: https://youtube.com/watch?v={video_id}")
    if args.publish_at:
        print("Status: scheduled (private until publish time)")


if __name__ == "__main__":
    main()
