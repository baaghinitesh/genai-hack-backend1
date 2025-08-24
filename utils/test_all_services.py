import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_story_service import test_story_service
from test_storage_service import test_storage_service
from test_image_service import test_image_generation
from test_audio_service import run_audio_tests
from loguru import logger


def main():
    """Test all services in sequence."""
    print("🚀 Testing All Services")
    print("=" * 50)
    
    results = {}
    
    # Test 1: ChatVertexAI (Story Service)
    print("\n1️⃣  Testing ChatVertexAI (Story Service)...")
    results['story'] = test_story_service()
    
    # Test 2: Storage Service
    print("\n2️⃣  Testing Storage Service...")
    results['storage'] = asyncio.run(test_storage_service())
    
    # Test 3: Image Service
    print("\n3️⃣  Testing Image Service...")
    results['image'] = asyncio.run(test_image_generation())
    
    # Test 4: Audio Services
    print("\n4️⃣  Testing Audio Services...")
    results['audio'] = asyncio.run(run_audio_tests())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for service, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{service.upper()} Service: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Your AI pipeline is ready!")
        print("\nNext steps:")
        print("1. Run the backend: python start_backend.py")
        print("2. Run the frontend: python start_frontend.py")
        print("3. Test the complete workflow")
    else:
        print("⚠️  SOME TESTS FAILED - Please check the logs above")
        print("\nFailed tests need to be fixed before the pipeline will work properly.")
    
    return all_passed


if __name__ == "__main__":
    main()
