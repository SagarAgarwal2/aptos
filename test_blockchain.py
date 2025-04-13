from blockchain import BlockchainManager
import os
import time

def test_blockchain_integration():
    """Test the blockchain integration."""
    print("Starting blockchain integration test...")
    print("Note: Running in simulation mode since no private keys are provided\n")
    
    try:
        # Initialize blockchain manager
        blockchain = BlockchainManager()
        print("✓ BlockchainManager initialized successfully")
        
        # Test student registration
        print("\n1. Testing student registration...")
        student_address = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        result = blockchain.register_student(student_address)
        if result["success"]:
            print("✓ Student registration successful")
            print(f"Transaction Hash: {result['transaction_hash']}")
            print(f"Message: {result['message']}")
        else:
            print(f"✗ Student registration failed: {result.get('error', 'Unknown error')}")
        
        # Test lesson creation
        print("\n2. Testing lesson creation...")
        result = blockchain.create_lesson(
            "Test Lesson",
            "This is a test lesson",
            10
        )
        if result["success"]:
            print("✓ Lesson creation successful")
            print(f"Transaction Hash: {result['transaction_hash']}")
            print(f"Message: {result['message']}")
        else:
            print(f"✗ Lesson creation failed: {result.get('error', 'Unknown error')}")
        
        # Test lesson completion
        print("\n3. Testing lesson completion...")
        sender_address = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        result = blockchain.complete_lesson(
            student_address,
            0,  # First lesson
            sender_address
        )
        if result["success"]:
            print("✓ Lesson completion successful")
            print(f"Transaction Hash: {result['transaction_hash']}")
            print(f"Message: {result['message']}")
        else:
            print(f"✗ Lesson completion failed: {result.get('error', 'Unknown error')}")
        
        # Test getting student progress
        print("\n4. Testing getting student progress...")
        result = blockchain.get_student_progress(student_address)
        if result["success"]:
            print("✓ Got student progress successfully")
            print(f"Data: {result['data']}")
            if 'message' in result:
                print(f"Message: {result['message']}")
        else:
            print(f"✗ Failed to get student progress: {result.get('error', 'Unknown error')}")
        
        # Test getting lesson details
        print("\n5. Testing getting lesson details...")
        result = blockchain.get_lesson(0)
        if result and result.get("success"):
            print("✓ Got lesson details successfully")
            print(f"Data: {result['data']}")
        else:
            print("✗ Failed to get lesson details")
            if result and 'error' in result:
                print(f"Error: {result['error']}")
        
        print("\n✓ Blockchain integration test completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_blockchain_integration() 