import pytest
from unittest.mock import Mock, patch
from storage import save_llms_txt

@pytest.mark.asyncio
async def test_save_llms_txt_no_config():
    log = Mock()
    with patch('storage.settings') as mock_settings:
        mock_settings.r2_endpoint = None
        result = await save_llms_txt("https://example.com", "content", log)
        assert result is None
        log.assert_called_once()
