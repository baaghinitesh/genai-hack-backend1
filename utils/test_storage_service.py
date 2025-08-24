import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.storage_service import storage_service
from loguru import logger


async def test_storage_service():
    """Test storage service."""
    try:
        logger.info("Testing storage service...")
        
        # Test bucket access
        bucket_access = await storage_service.check_bucket_access()
        
        if bucket_access:
            logger.success("✅ Storage service bucket access successful!")
            
            # Test uploading a simple file
            test_data = b"This is a test file for storage service"
            test_filename = "test/test_file.txt"
            
            logger.info("Testing file upload...")
            url = await storage_service.upload_bytes(test_data, test_filename, "text/plain")
            
            if url:
                logger.success(f"✅ File upload successful! URL: {url}")
                return True
            else:
                logger.error("❌ File upload failed")
                return False
        else:
            logger.error("❌ Storage service bucket access failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Storage service test failed: {e}")
        return False


if __name__ == "__main__":
    print("☁️  Testing Storage Service")
    print("=" * 50)
    
    result = asyncio.run(test_storage_service())
    
    if result:
        print("\n✅ Storage service test PASSED")
    else:
        print("\n❌ Storage service test FAILED")
