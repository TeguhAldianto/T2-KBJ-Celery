from tasks import test_task

if __name__ == "__main__":
    message = "Pengujian Job Queue KBJ S2 Informatika UNESA"

    print("PRODUCER: Mengirim pekerjaan...")

    result = test_task.delay(message)

    print(f"Task ID: {result.id}")
    print("PRODUCER: Pekerjaan berhasil dikirim.")

    try:
        output = result.get(timeout=30)
        print("\nHASIL EKSEKUSI:")
        print(output)
    except Exception as error:
        print(f"Pengujian gagal: {error}")