import pytest
import time

BASE_URL = "https://opm-website.iot-asm-test1.insitech.live"
API_TIMEOUT = 2


class TestShopsApi:
    @pytest.mark.parametrize("test_case", [
        ("success", "post", "/api/map/shops", {}, 200, None, False),
        ("invalid_method", "get", "/api/map/shops", None, 405, None, False),
        ("invalid_content_type", "post", "/api/map/shops", "not json", 415, {"Content-Type": "text/plain"}, False),
        ("unauthorized", "post", "/api/map/shops", {}, 401, None, True),
        ("not_found", "post", "/api/non_existent_endpoint", {}, 404, None, False),
    ])
    def test_api_status_codes(self, api_session, requests, test_case):
        """Проверка различных статус-кодов API."""
        case_name, method, endpoint, data, expected_status, headers, use_clean_session = test_case
        session = requests if use_clean_session else api_session
        url = f"{BASE_URL}{endpoint}"

        request_func = getattr(session, method)
        if method == "get":
            response = request_func(url, headers=headers)
        else:
            response = request_func(url, json=data, headers=headers) if headers else request_func(url, data=data)

        assert response.status_code == expected_status, f"Для случая '{case_name}' ожидался код {expected_status}, получен {response.status_code}"

    @pytest.mark.parametrize("invalid_data", [
        {"invalid_key": "value"},
        {"pageSize": "not_a_number"},
        {"pageSize": -1}
    ])
    def test_invalid_request_data(self, api_session, invalid_data):
        """Проверка реакции API на некорректные данные запроса."""
        response = api_session.post(f"{BASE_URL}/api/map/shops", json=invalid_data)
        assert response.status_code == 400, f"Ожидался код 400, получен {response.status_code}"

    def test_shops_data_structure(self, api_session):
        """Проверка структуры данных магазинов в ответе API."""
        response = api_session.post(f"{BASE_URL}/api/map/shops", json={})
        assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"

        shops = response.json()
        assert isinstance(shops, list), "Ответ должен быть списком"
        assert len(shops) > 0, "Список магазинов не должен быть пустым"

        required_fields = ['id', 'partnerId', 'name', 'longitude', 'latitude', 'address', 'workTime', 'quantity',
                           'existThing', 'needPromocode']
        for shop in shops[:5]:  # Проверяем первые 5 магазинов @TODO
            for field in required_fields:
                assert field in shop, f"Поле '{field}' отсутствует в данных магазина"

    def test_coordinates_validity(self, api_session):
        """Проверка валидности координат магазинов."""
        response = api_session.post(f"{BASE_URL}/api/map/shops", json={})
        shops = response.json()
        for shop in shops[:10]:  # Проверяем первые 10 магазинов
            longitude = float(shop['longitude'])
            latitude = float(shop['latitude'])
            assert -180 <= longitude <= 180, f"Неверная долгота: {longitude}"
            assert -90 <= latitude <= 90, f"Неверная широта: {latitude}"

    def test_work_time_format(self, api_session):
        """Проверка формата рабочего времени магазинов."""
        response = api_session.post(f"{BASE_URL}/api/map/shops", json={})
        shops = response.json()
        for shop in shops[:10]:  # Проверяем первые 10 магазинов
            work_time = shop['workTime']
            assert ' - ' in work_time, f"Неверный формат рабочего времени: {work_time}"
            start, end = work_time.split(' - ')
            assert self.is_valid_time(start) and self.is_valid_time(end), f"Неверное время: {work_time}"

    @staticmethod
    def is_valid_time(time_str):
        """Проверка валидности строки времени."""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return 0 <= hours < 24 and 0 <= minutes < 60
        except ValueError:
            return False

    @pytest.mark.parametrize("shop_name", ["Билайн Калейдоскоп", "М.Видео Авеню Юго-Западная"])
    def test_specific_shop_presence(self, api_session, shop_name):
        """Проверка наличия конкретных магазинов в списке."""
        response = api_session.post(f"{BASE_URL}/api/map/shops", json={})
        shops = response.json()
        assert any(shop['name'] == shop_name for shop in shops), f"Магазин '{shop_name}' не найден"

    @pytest.mark.performance
    def test_response_time(self, api_session):
        """Проверка времени ответа API."""
        start_time = time.time()
        api_session.post(f"{BASE_URL}/api/map/shops", json={})
        end_time = time.time()
        assert end_time - start_time < API_TIMEOUT, f"Время ответа превышает {API_TIMEOUT} секунды"