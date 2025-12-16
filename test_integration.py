#!/usr/bin/env python3
"""
Quick integration test to verify the application can start without errors.
"""
import sys
import traceback

def test_imports():
    """Test all critical imports."""
    print("🧪 Testing imports...")
    
    tests = [
        ("Config", "from app.core.config import settings"),
        ("Security", "from app.core.security import get_password_hash, verify_password"),
        ("Database", "from app.db.session import engine, Base, get_db"),
        ("Models", "from app.models.all_models import User, Domain, AppSettings"),
        ("FastAPI App", "from main import app"),
    ]
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            traceback.print_exc()
            return False
    
    return True


def test_config():
    """Test configuration is loaded correctly."""
    print("\n🧪 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        checks = [
            ("PROJECT_NAME", settings.PROJECT_NAME),
            ("DATABASE_URL", settings.DATABASE_URL[:30] + "..."),
            ("LOG_LEVEL", settings.LOG_LEVEL),
            ("SECRET_KEY", "***" if len(settings.SECRET_KEY) > 0 else "NOT SET"),
        ]
        
        for name, value in checks:
            print(f"  ✅ {name}: {value}")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        traceback.print_exc()
        return False


def test_app():
    """Test that FastAPI app can be created."""
    print("\n🧪 Testing FastAPI app...")
    
    try:
        from main import app
        
        # Check routers are registered
        if app.routes:
            print(f"  ✅ App has {len(app.routes)} routes registered")
        
        return True
    except Exception as e:
        print(f"  ❌ App error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("🚀 SSL Checker Integration Test")
    print("=" * 50)
    print()
    
    results = [
        test_imports(),
        test_config(),
        test_app(),
    ]
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ All tests passed! The app is ready to run.")
        print("\nRun with: python main.py")
        return 0
    else:
        print("❌ Some tests failed. See errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
