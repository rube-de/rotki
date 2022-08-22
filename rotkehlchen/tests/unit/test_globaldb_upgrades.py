import pytest

from rotkehlchen.assets.types import AssetType
from rotkehlchen.constants.resolver import ETHEREUM_DIRECTIVE, ChainID
from rotkehlchen.types import ChecksumEvmAddress, EvmTokenKind


def _old_ethaddress_to_identifier(address: ChecksumEvmAddress) -> str:
    return ETHEREUM_DIRECTIVE + address


def _old_strethaddress_to_identifier(address: str) -> str:
    return ETHEREUM_DIRECTIVE + address


@pytest.mark.parametrize('globaldb_version', [2])
@pytest.mark.parametrize('target_globaldb_version', [3])
def test_upgrade_v2_v3(globaldb):
    """At the start of this test global DB is upgraded to v3"""
    assert globaldb.get_setting_value('version', None) == 3
    with globaldb.conn.read_ctx() as cursor:
        # test that we have the same number of assets before and after the migration
        # 367 are the new assets from other chains that are evm and currently they are
        # marked with the OTHER asset type or that are missing the different chains versions.
        # 38 are the assets with type OTHER that will be replaced
        assert cursor.execute('SELECT COUNT(*) from assets').fetchone()[0] == 3095 + 720 - 106

        # Check that the properties of LUSD (ethereum token) have been correctly translated
        weth_token_data = cursor.execute('SELECT identifier, token_kind, chain, address, decimals, protocol FROM evm_tokens WHERE address = "0x5f98805A4E8be255a32880FDeC7F6728C6568bA0"').fetchone()  # noqa: E501
        assert weth_token_data[0] == 'eip155:1/erc20:0x5f98805A4E8be255a32880FDeC7F6728C6568bA0'
        assert EvmTokenKind.deserialize_from_db(weth_token_data[1]) == EvmTokenKind.ERC20
        assert ChainID.deserialize_from_db(weth_token_data[2]) == ChainID.ETHEREUM
        assert weth_token_data[3] == '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0'
        assert weth_token_data[4] == 18
        assert weth_token_data[5] is None
        weth_asset_data = cursor.execute('SELECT name, symbol, coingecko, cryptocompare, forked FROM common_asset_details WHERE identifier = "eip155:1/erc20:0x5f98805A4E8be255a32880FDeC7F6728C6568bA0"').fetchone()  # noqa: E501
        assert weth_asset_data[0] == 'LUSD Stablecoin'
        assert weth_asset_data[1] == 'LUSD'
        assert weth_asset_data[2] == 'liquity-usd'
        assert weth_asset_data[3] == 'LUSD'
        assert weth_asset_data[4] is None
        weth_asset_data = cursor.execute('SELECT type, started, swapped_for FROM assets WHERE identifier = "eip155:1/erc20:0x5f98805A4E8be255a32880FDeC7F6728C6568bA0"').fetchone()  # noqa: E501
        assert AssetType.deserialize_from_db(weth_asset_data[0]) == AssetType.EVM_TOKEN
        assert weth_asset_data[1] == 1617611299
        assert weth_asset_data[2] is None

        # Check that a normal asset also gets correctly mapped
        weth_asset_data = cursor.execute('SELECT name, symbol, coingecko, cryptocompare, forked FROM common_asset_details WHERE identifier = "BCH"').fetchone()  # noqa: E501
        assert weth_asset_data[0] == 'Bitcoin Cash'
        assert weth_asset_data[1] == 'BCH'
        assert weth_asset_data[2] == 'bitcoin-cash'
        assert weth_asset_data[3] is None
        assert weth_asset_data[4] == 'BTC'
        weth_asset_data = cursor.execute('SELECT type, started, swapped_for FROM assets WHERE identifier = "BCH"').fetchone()  # noqa: E501
        assert AssetType.deserialize_from_db(weth_asset_data[0]) == AssetType.OWN_CHAIN
        assert weth_asset_data[1] == 1501593374
        assert weth_asset_data[2] is None

        ids_in_db = {row[0] for row in cursor.execute('SELECT * FROM user_owned_assets')}
        assert ids_in_db == {
            'eip155:1/erc20:0x4E15361FD6b4BB609Fa63C81A2be19d873717870',
            'eip155:1/erc20:0x429881672B9AE42b8EbA0E26cD9C73711b891Ca5',
            'eip155:1/erc20:0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0',
            'BTC',
            'ETH',
            'USD',
            'EUR',
            'BCH',
        }
