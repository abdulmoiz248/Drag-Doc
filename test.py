#!/usr/bin/env python3
"""
Test script for the Enhanced RAG Documentation System
Handles upload and documentation generation with proper error handling
"""

import requests
import os
import time
import sys
from pathlib import Path

class DocumentationTester:
    def __init__(self, base_url="http://localhost:8000", backend_path="backend"):
        self.base_url = base_url
        self.backend_path = backend_path
        self.session = requests.Session()
        
    def check_server_status(self):
        """Check if the FastAPI server is running"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Server is running!")
                print(f"📋 Server info: {response.json()}")
                return True
            else:
                print(f"⚠️ Server responded with status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server!")
            print("💡 Make sure to start the server first:")
            print("   cd backend")
            print("   python main.py")
            return False
        except Exception as e:
            print(f"❌ Error checking server: {e}")
            return False
    
    def find_sample_zip(self):
        """Find the sample.zip file in the project structure"""
        possible_paths = [
            os.path.join(self.backend_path, "data", "sample.zip"),
            "sample.zip",
            os.path.join("data", "sample.zip"),
            os.path.join(self.backend_path, "sample.zip")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"📁 Found sample.zip at: {path}")
                return path
        
        print("❌ sample.zip not found in expected locations:")
        for path in possible_paths:
            print(f"   - {path}")
        return None
    
    def upload_project(self, zip_path):
        """Upload the zip file to the server"""
        print(f"\n🚀 Uploading project: {zip_path}")
        
        try:
            with open(zip_path, "rb") as f:
                files = {"file": f}
                response = self.session.post(f"{self.base_url}/upload-zip/", files=files)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Upload successful!")
                print(f"📊 Files processed: {data.get('files_processed', 'N/A')}")
                print(f"🔗 Chunks created: {data.get('chunks_created', 'N/A')}")
                print(f"🆔 Session ID: {data['session_id']}")
                return data["session_id"]
            else:
                print(f"❌ Upload failed with status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return None
                
        except FileNotFoundError:
            print(f"❌ File not found: {zip_path}")
            return None
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return None
    
    def check_session_status(self, session_id):
        """Check the status of a session"""
        try:
            response = self.session.get(f"{self.base_url}/session-info/{session_id}")
            if response.status_code == 200:
                data = response.json()
                print(f"📋 Session Status: {data.get('status')}")
                print(f"📁 Files count: {data.get('files_count')}")
                print(f"🔗 Vector store ready: {data.get('vector_store_ready')}")
                return True
            else:
                print(f"⚠️ Session check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Session check error: {e}")
            return False
    
    def generate_documentation(self, session_id, output_filename="enhanced_documentation.pdf"):
        """Generate comprehensive documentation"""
        print(f"\n📚 Generating comprehensive documentation...")
        print("⏳ This may take a few minutes for large projects...")
        
        try:
            # Make the documentation generation request
            response = self.session.get(
                f"{self.base_url}/api/v1/generate-documentation/",
                params={"session_id": session_id},
                stream=True,
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code == 200:
                # Save the PDF
                with open(output_filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(output_filename)
                print(f"✅ Documentation generated successfully!")
                print(f"📄 Saved as: {output_filename}")
                print(f"📊 File size: {file_size / 1024:.2f} KB")
                
                # Try to open the PDF (Windows)
                if sys.platform == "win32":
                    try:
                        os.startfile(output_filename)
                        print("🔍 Opening PDF in default viewer...")
                    except:
                        pass
                
                return True
            else:
                print(f"❌ Documentation generation failed!")
                print(f"📄 Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out - the project might be too large")
            print("💡 Try with a smaller project or increase the timeout")
            return False
        except Exception as e:
            print(f"❌ Documentation generation error: {e}")
            return False
    
    def test_basic_functionality(self, session_id):
        """Test other API endpoints"""
        print(f"\n🧪 Testing other API functionality...")
        
        # Test summary generation
        try:
            response = self.session.get(f"{self.base_url}/generate-summary/", params={"session_id": session_id})
            if response.status_code == 200:
                print("✅ Summary generation: Working")
            else:
                print("⚠️ Summary generation: Failed")
        except Exception as e:
            print(f"❌ Summary test error: {e}")
        
        # Test MCQ generation
        try:
            response = self.session.get(f"{self.base_url}/generate-mcqs/", params={"session_id": session_id})
            if response.status_code == 200:
                data = response.json()
                mcq_count = len(data.get('mcqs', []))
                print(f"✅ MCQ generation: Working ({mcq_count} questions)")
            else:
                print("⚠️ MCQ generation: Failed")
        except Exception as e:
            print(f"❌ MCQ test error: {e}")
    
    def run_full_test(self, zip_path=None):
        """Run the complete test suite"""
        print("🚀 Enhanced RAG Documentation System - Test Suite")
        print("=" * 60)
        
        # Step 1: Check server
        if not self.check_server_status():
            return False
        
        # Step 2: Find zip file
        if zip_path is None:
            zip_path = self.find_sample_zip()
            if zip_path is None:
                return False
        
        # Step 3: Upload project
        session_id = self.upload_project(zip_path)
        if session_id is None:
            return False
        
        # Step 4: Check session
        if not self.check_session_status(session_id):
            return False
        
        # Step 5: Test basic functionality
        self.test_basic_functionality(session_id)
        
        # Step 6: Generate documentation
        success = self.generate_documentation(session_id)
        
        if success:
            print("\n🎉 All tests completed successfully!")
            print("📋 Summary:")
            print(f"   - Session ID: {session_id}")
            print(f"   - Project: {os.path.basename(zip_path)}")
            print(f"   - Documentation: enhanced_documentation.pdf")
        else:
            print("\n❌ Test suite completed with errors")
        
        return success

def main():
    """Main function"""
    print("Enhanced RAG Documentation System - Test Script")
    print("=" * 50)
    
    # Initialize tester
    tester = DocumentationTester()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        zip_path = sys.argv[1]
        if not os.path.exists(zip_path):
            print(f"❌ File not found: {zip_path}")
            return
        print(f"📁 Using provided zip file: {zip_path}")
        tester.run_full_test(zip_path)
    else:
        # Run with auto-detection
        tester.run_full_test()

if __name__ == "__main__":
    main()
