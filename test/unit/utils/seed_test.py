from unittest.mock import patch

from kiwi.utils.seed import generate_seed_uuid


class TestSeed:
    def test_generate_seed_uuid(self):
        with patch.dict('os.environ', {'SOURCE_DATE_EPOCH': '123456'}):
            assert generate_seed_uuid('label') == \
                'c0cbf4e3-10a7-86ea-9472-87aaca0074f2'

    def test_generate_seed_uuid_is_stable(self):
        with patch.dict('os.environ', {'SOURCE_DATE_EPOCH': '123456'}):
            assert generate_seed_uuid('label') == generate_seed_uuid('label')

    def test_generate_seed_uuid_differs_per_name(self):
        with patch.dict('os.environ', {'SOURCE_DATE_EPOCH': '123456'}):
            assert generate_seed_uuid('1:p.UEFI') != \
                generate_seed_uuid('2:p.lxroot')

    @patch('kiwi.utils.seed.uuid')
    def test_generate_seed_uuid_random(self, mock_uuid):
        mock_uuid.uuid4.return_value = 'some'
        with patch.dict('os.environ', {'SOURCE_DATE_EPOCH': ''}):
            assert generate_seed_uuid('label') == 'some'
