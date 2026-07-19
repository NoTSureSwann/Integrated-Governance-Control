import unittest
import requests
from services.connection_manager import ConnectionManager, SQLiteConnectionPool

class TestConnectionManager(unittest.TestCase):
    """
    Test Case untuk memverifikasi SQLite pooling dan retry Exponential Backoff.
    """
    def setUp(self):
        self.manager = ConnectionManager()

    def test_sqlite_connection_pooling(self):
        """Memastikan koneksi diambil dan dilepaskan kembali ke pool SQLite secara tepat."""
        pool = SQLiteConnectionPool("database/test_nexus.db", max_connections=2)
        
        # Ambil koneksi pertama
        conn1 = pool.get_connection()
        self.assertIsNotNone(conn1)
        self.assertEqual(pool._created, 1)

        # Ambil koneksi kedua
        conn2 = pool.get_connection()
        self.assertIsNotNone(conn2)
        self.assertEqual(pool._created, 2)
        
        # Kembalikan koneksi pertama
        pool.release_connection(conn1)
        self.assertEqual(pool.pool.qsize(), 1)
        
        # Bersihkan koneksi
        conn2.close()

    def test_pooled_connection_proxy_close(self):
        """Memastikan calling close() pada PooledConnectionProxy mengembalikan koneksi ke pool."""
        conn = self.manager.get_sqlite_connection()
        
        # Jalankan query SELECT 1 sederhana
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        val = cursor.fetchone()[0]
        self.assertEqual(val, 1)
        
        # Cek jumlah antrian pool sebelum ditutup
        qsize_before = self.manager.sqlite_pool.pool.qsize()
        
        # Panggil close() -> Ini harus memicu rilis ke pool, bukan close fisik SQLite
        conn.close()
        
        qsize_after = self.manager.sqlite_pool.pool.qsize()
        self.assertEqual(qsize_after, qsize_before + 1)

    def test_exponential_backoff_retry_success(self):
        """Menguji pemanggilan HTTP dengan retry backoff yang akhirnya sukses."""
        from unittest.mock import patch, MagicMock
        
        url = "https://api.groq.com/v1/ping"
        
        # Simulasikan 2 kali kegagalan koneksi (503 Service Unavailable), lalu sukses pada percobaan ke-3
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 503
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"status": "ok"}
        
        with patch("requests.request") as mock_request:
            mock_request.side_effect = [
                mock_response_fail,
                mock_response_fail,
                mock_response_success
            ]
            
            # Gunakan base_delay = 0.01 agar test berjalan sangat cepat tanpa jeda panjang
            res = self.manager.request_with_retry(url, method="GET", max_retries=3, base_delay=0.01)
            
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "ok")
            self.assertEqual(mock_request.call_count, 3)

if __name__ == "__main__":
    unittest.main()
