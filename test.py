import requests
import os
import sys

def upload_and_generate_doc(
    base_url="http://localhost:8000",
    zip_path="backend/data/sample2.zip",
    output_filename="documentation.pdf"
):
    if not os.path.exists(zip_path):
        print(f"❌ File not found: {zip_path}")
        return False

    session = requests.Session()

    # Upload the zip file
    print(f"🚀 Uploading {zip_path} ...")
    try:
        with open(zip_path, "rb") as f:
            files = {"file": f}
            response = session.post(f"{base_url}/upload-zip/", files=files)
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            print(f"✅ Uploaded! Session ID: {session_id}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

    # Generate documentation PDF
    print("📚 Generating documentation PDF...")
    try:
        response = session.get(
            f"{base_url}/generate-documentation/",
            params={"session_id": session_id},
            stream=True,
            timeout=300
        )
        if response.status_code == 200:
            with open(output_filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            file_size = os.path.getsize(output_filename)
            print(f"✅ Documentation PDF generated!")
            print(f"📄 Saved as: {output_filename}")
            print(f"📊 File size: {file_size / 1024:.2f} KB")
            if sys.platform == "win32":
                try:
                    os.startfile(output_filename)
                    print("🔍 Opening PDF in default viewer...")
                except Exception:
                    pass
            return True
        else:
            print(f"❌ Documentation PDF generation failed! Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Documentation PDF generation error: {e}")
        return False

if __name__ == "__main__":
    upload_and_generate_doc()
