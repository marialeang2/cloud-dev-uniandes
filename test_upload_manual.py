"""
Script manual para probar el endpoint de upload de videos.
Asegúrate de que el servidor esté corriendo: uvicorn app.main:app --reload
"""
import requests
from pathlib import Path
import sys


def test_upload():
    """Test manual del endpoint de upload"""
    
    BASE_URL = "http://localhost:8000"
    
    # Verificar que el video existe
    video_path = Path("tests/test_data/flex.mp4")
    if not video_path.exists():
        print("❌ Error: Video flex.mp4 no encontrado en tests/test_data/")
        return False
    
    print("🎥 Probando endpoint de upload de video...\n")
    print(f"   Video: {video_path}")
    print(f"   Tamaño: {video_path.stat().st_size / (1024*1024):.2f} MB\n")
    
    # Primero crear un usuario de prueba
    print("1️⃣  Creando usuario de prueba...")
    user_data = {
        "first_name": "Test",
        "last_name": "Upload",
        "email": f"test_upload_{Path(__file__).stat().st_mtime}@example.com",
        "password1": "TestPass123",
        "password2": "TestPass123",
        "city": "Bogotá",
        "country": "Colombia"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=user_data, timeout=10)
        if response.status_code == 201:
            user_id = response.json()["user_id"]
            print(f"   ✅ Usuario creado: {user_id}\n")
        else:
            print(f"   ❌ Error al crear usuario: {response.status_code}")
            print(f"      {response.json()}\n")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Error: No se puede conectar al servidor")
        print("      ¿Está corriendo? uvicorn app.main:app --reload\n")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}\n")
        return False
    
    # Subir el video
    print("2️⃣  Subiendo video...")
    
    with open(video_path, "rb") as f:
        files = {
            "video_file": ("flex.mp4", f, "video/mp4")
        }
        data = {
            "title": "Mi Video de Prueba - Flex",
            "user_id": user_id
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/videos/upload",
                files=files,
                data=data,
                timeout=30  # Upload puede tardar
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.json()}\n")
            
            if response.status_code == 201:
                video_id = response.json()["video_id"]
                print(f"   ✅ Video subido exitosamente!")
                print(f"      Video ID: {video_id}\n")
                
                # Verificar que se puede obtener el video
                print("3️⃣  Verificando video subido...")
                response = requests.get(
                    f"{BASE_URL}/api/videos/{video_id}",
                    params={"user_id": user_id}
                )
                
                if response.status_code == 200:
                    video_data = response.json()
                    print(f"   ✅ Video encontrado:")
                    print(f"      Título: {video_data.get('title')}")
                    print(f"      Duración: {video_data.get('duration_seconds')} segundos")
                    print(f"      Status: {video_data.get('status')}")
                    print(f"      Público: {video_data.get('is_public')}")
                    print(f"      Votos: {video_data.get('votes')}\n")
                    return True
                else:
                    print(f"   ⚠️  No se pudo verificar el video: {response.status_code}\n")
                    return True  # Upload funcionó, pero no se pudo verificar
            else:
                print(f"   ❌ Error al subir video")
                print(f"      Detalles: {response.json()}\n")
                return False
                
        except requests.exceptions.Timeout:
            print("   ⚠️  Timeout - el upload tomó más de 30 segundos")
            print("      Esto puede ser normal para videos grandes o si FFmpeg es lento\n")
            return False
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}\n")
            return False


if __name__ == "__main__":
    print("═══════════════════════════════════════════════════════════")
    print("   🧪 PRUEBA MANUAL DEL ENDPOINT DE UPLOAD")
    print("═══════════════════════════════════════════════════════════\n")
    
    success = test_upload()
    
    print("═══════════════════════════════════════════════════════════")
    if success:
        print("   ✅ PRUEBA EXITOSA")
    else:
        print("   ❌ PRUEBA FALLIDA")
    print("═══════════════════════════════════════════════════════════\n")
    
    sys.exit(0 if success else 1)

