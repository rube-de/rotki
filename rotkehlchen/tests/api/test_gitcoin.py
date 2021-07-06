from http import HTTPStatus

import pytest
import requests

from rotkehlchen.chain.ethereum.gitcoin.constants import GITCOIN_GRANTS_PREFIX
from rotkehlchen.db.ledger_actions import DBLedgerActions
from rotkehlchen.tests.utils.api import (
    api_url_for,
    assert_error_response,
    assert_proper_response,
    assert_proper_response_with_result,
)
from rotkehlchen.typing import Location


@pytest.mark.parametrize('start_with_valid_premium', [True, False])
@pytest.mark.parametrize('number_of_eth_accounts', [0])
def test_get_grant_events(rotkehlchen_api_server, start_with_valid_premium):
    grant_id = 149  # rotki grant
    json_data = {
        'from_timestamp': 1622516400,  # 3 hours hours after midnight 01/06/2021
        'to_timestamp': 1623294000,  # 3 hours hours after midnight 10/06/2021
        'grant_id': grant_id,
    }
    response = requests.post(api_url_for(
        rotkehlchen_api_server,
        'gitcoineventsresource',
    ), json=json_data)
    if start_with_valid_premium is False:
        assert_error_response(
            response=response,
            contained_in_msg='does not have a premium subscription',
            status_code=HTTPStatus.CONFLICT,
        )
        return

    outcome = assert_proper_response_with_result(response)
    assert len(outcome) == 34
    assert outcome[:5] == [{
        'amount': '0.000475',
        'asset': 'ETH',
        'clr_round': None,
        'grant_id': grant_id,
        'timestamp': 1622518496,
        'tx_id': '8ee8bfe2d07a0a9192549725aa3d3dcf78b7913a6bf187895c2510fb058ed314',
        'tx_type': 'zksync',
        'usd_value': '1.25121175',
    }, {
        'amount': '0.000475',
        'asset': 'ETH',
        'clr_round': None,
        'grant_id': grant_id,
        'timestamp': 1622603572,
        'tx_id': 'b75d5a7b7073a8d306492641955106145a16728250243c6ed86c205857b75807',
        'tx_type': 'zksync',
        'usd_value': '1.28526450',
    }, {
        'amount': '0.95',
        'asset': '_ceth_0xdAC17F958D2ee523a2206206994597C13D831ec7',
        'clr_round': None,
        'grant_id': grant_id,
        'timestamp': 1622710976,
        'tx_id': 'ebc0b230114c13fdd8957e01e0568a34928c87c89b9d0f8a0db058849e9419ef',
        'tx_type': 'zksync',
        'usd_value': '0.95',
    }, {
        'amount': '0.00019',
        'asset': 'ETH',
        'clr_round': None,
        'grant_id': grant_id,
        'timestamp': 1622711531,
        'tx_id': 'f9e25d11eb88a644bed9c40902fe76e64fa4b4c3fe3a8a7bfefad10559a08e12',
        'tx_type': 'zksync',
        'usd_value': '0.5335006159891',
    }, {
        'amount': '1.9',
        'asset': '_ceth_0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        'clr_round': None,
        'grant_id': grant_id,
        'timestamp': 1622737471,
        'tx_id': '0xb632c6f0b2d9aed0924cefc62cc47b8258d373122c66f8ad4a1c37d2b5f7f0ff',
        'tx_type': 'ethereum',
        'usd_value': '1.900000000000000099999999999',
    }]
    assert outcome[-1] == {
        'amount': '0.95',
        'asset': '_ceth_0x6B175474E89094C44Da98b954EedeAC495271d0F',
        'clr_round': None,
        'grant_id': grant_id,
        'timestamp': 1623250357,
        'tx_id': 'e2e2d8f24696a8dacbb5edceae718ef6b29a59123ed6e1d663ef9159c231b361',
        'tx_type': 'zksync',
        'usd_value': '0.9499999999999998000000000000',
    }


@pytest.mark.parametrize('start_with_valid_premium', [True])
@pytest.mark.parametrize('number_of_eth_accounts', [0])
def test_delete_grant_events(rotkehlchen_api_server):
    rotki = rotkehlchen_api_server.rest_api.rotkehlchen
    # Get and save data of 3 different grants in the DB
    id1 = 149
    json_data = {
        'from_timestamp': 1622162468,  # 28/05/2021
        'to_timestamp': 1622246400,  # 29/05/2021
        'grant_id': id1,
    }
    response = requests.post(api_url_for(
        rotkehlchen_api_server,
        'gitcoineventsresource',
    ), json=json_data)
    assert_proper_response(response)
    id2 = 184
    json_data = {
        'from_timestamp': 1622162468,  # 28/05/2021
        'to_timestamp': 1622246400,  # 29/05/2021
        'grant_id': id2,
    }
    response = requests.post(api_url_for(
        rotkehlchen_api_server,
        'gitcoineventsresource',
    ), json=json_data)
    assert_proper_response(response)
    id3 = 223
    json_data = {
        'from_timestamp': 1622162468,  # 28/05/2021
        'to_timestamp': 1622246400,  # 29/05/2021
        'grant_id': id3,
    }
    response = requests.post(api_url_for(
        rotkehlchen_api_server,
        'gitcoineventsresource',
    ), json=json_data)
    assert_proper_response(response)

    # make sure events are saved
    db = rotki.data.db
    ledgerdb = DBLedgerActions(db, db.msg_aggregator)
    actions = ledgerdb.get_ledger_actions(from_ts=None, to_ts=None, location=Location.GITCOIN)
    assert len(actions) == 5
    assert len([x for x in actions if x.extra_data.grant_id == id1]) == 3
    assert len([x for x in actions if x.extra_data.grant_id == id2]) == 1
    assert len([x for x in actions if x.extra_data.grant_id == id3]) == 1
    # make sure db ranges were written
    queryrange = db.get_used_query_range(f'{GITCOIN_GRANTS_PREFIX}_{id1}')
    assert queryrange == (1622162468, 1622246400)
    queryrange = db.get_used_query_range(f'{GITCOIN_GRANTS_PREFIX}_{id2}')
    assert queryrange == (1622162468, 1622246400)
    queryrange = db.get_used_query_range(f'{GITCOIN_GRANTS_PREFIX}_{id3}')
    assert queryrange == (1622162468, 1622246400)

    # delete 1 grant's data
    response = requests.delete(api_url_for(
        rotkehlchen_api_server,
        'gitcoineventsresource',
    ), json={'grant_id': id2})
    assert_proper_response(response)
    # check that they got deleted but rest is fine
    actions = ledgerdb.get_ledger_actions(from_ts=None, to_ts=None, location=Location.GITCOIN)
    assert len(actions) == 4
    assert len([x for x in actions if x.extra_data.grant_id == id1]) == 3
    assert len([x for x in actions if x.extra_data.grant_id == id2]) == 0
    assert len([x for x in actions if x.extra_data.grant_id == id3]) == 1
    # make sure db ranges were written
    queryrange = db.get_used_query_range(f'{GITCOIN_GRANTS_PREFIX}_{id1}')
    assert queryrange == (1622162468, 1622246400)
    assert db.get_used_query_range(f'{GITCOIN_GRANTS_PREFIX}_{id2}') is None
    queryrange = db.get_used_query_range(f'{GITCOIN_GRANTS_PREFIX}_{id3}')
    assert queryrange == (1622162468, 1622246400)

    # delete all remaining grant data
    response = requests.delete(api_url_for(
        rotkehlchen_api_server,
        'gitcoineventsresource',
    ))
    assert_proper_response(response)
    # check that they got deleted but rest is fine
    actions = ledgerdb.get_ledger_actions(from_ts=None, to_ts=None, location=Location.GITCOIN)
    assert len(actions) == 0
    # make sure db ranges were written
    assert db.get_used_query_range(f'{GITCOIN_GRANTS_PREFIX}_{id1}') is None
    assert db.get_used_query_range(f'{GITCOIN_GRANTS_PREFIX}_{id2}') is None
    assert db.get_used_query_range(f'{GITCOIN_GRANTS_PREFIX}_{id3}') is None