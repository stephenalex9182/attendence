import requests
import sys

BASE_URL = "http://localhost:8000"

def run_tests():
    print("Running Verification Tests...")

    # 1. Check Root
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"Root: {r.status_code}") # Root returns HTML, not JSON
    except Exception as e:
        print(f"Failed to connect to backend: {e}")
        sys.exit(1)

    # 2. Login as Faculty
    print("\nLogging in as Faculty...")
    login_data = {"username": "ruthiwic@mlrit.ac.in", "password": "password123"}
    r = requests.post(f"{BASE_URL}/token", data=login_data)
    if r.status_code != 200:
        print(f"Login Failed: {r.text}")
        sys.exit(1)
    
    token = r.json()["access_token"]
    print("Login Successful. Token received.")
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Add a Student
    print("\nAdding valid student...")
    student_data = {
        "email": "24r21a66h5@mlrit.ac.in",
        "password": "password123",
        "role": "student",
        "roll_number": "24r21a66h5"
    }
    r = requests.post(f"{BASE_URL}/users/add", json=student_data, headers=headers)
    if r.status_code == 200:
        print(f"Student Added: {r.json()['email']}")
        student_id = r.json()['id']
    elif r.status_code == 400 and "already registered" in r.text:
       print("Student already exists (expected if re-running).")
       # Fetch to get ID
       r = requests.get(f"{BASE_URL}/users/students", headers=headers)
       for s in r.json():
           if s["email"] == student_data["email"]:
               student_id = s["id"]
               break
    else:
        print(f"Add Student Failed: {r.text}")
        sys.exit(1)

    # 4. Mark Attendance
    print("\nMarking Attendance...")
    import datetime
    today = datetime.date.today().isoformat()
    attendance_payload = [
        {"student_id": student_id, "date": today, "status": "present"}
    ]
    r = requests.post(f"{BASE_URL}/attendance/batch_upsert", json=attendance_payload, headers=headers)
    print(f"Mark Attendance: {r.status_code} - {r.json()}")

    # 5. Check Student Stats (Login as Student)
    print("\nLogging in as Student...")
    student_login = {"username": "24r21a66h5@mlrit.ac.in", "password": "password123"}
    r = requests.post(f"{BASE_URL}/token", data=student_login)
    student_token = r.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    print("Fetching Student Stats...")
    r = requests.get(f"{BASE_URL}/attendance/stats", headers=student_headers)
    print(f"Stats: {r.json()}")
    
    if r.json()["present"] >= 1:
        print("\nSUCCESS: Verification Complete!")
    else:
        print("\nFAILURE: Stats did not reflect attendance.")

    # 6. Check /users/me
    print("\nFetching Student Profile (/users/me)...")
    r = requests.get(f"{BASE_URL}/users/me", headers=student_headers)
    if r.status_code == 200:
        print(f"Profile: {r.json()}")
    else:
        print(f"Failed to fetch profile: {r.status_code}")


if __name__ == "__main__":
    run_tests()
