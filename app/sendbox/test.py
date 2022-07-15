from starknet_py.contract import Contract
from starknet_py.net import AccountClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starkware.starknet.public.abi_structs import identifier_manager_from_abi


private_key = 1234512345123451234511111

# acc_client = AccountClient.create_account_sync(
#     net="testnet", chain=StarknetChainId.TESTNET, private_key=private_key,
# )

# print(acc_client.address)
# print(acc_client.signer.private_key())
# print(acc_client.signer.public_key())


private_key = (
    3481907968109126366631341857992198869776879917929289470748436139290217987122
)
account_address = "0x06C55071C86Bc33c0C8d95A03190941641e664C43c228E0B0389F6566BDf0965"

key_pair = KeyPair.from_private_key(private_key)

acc_client = AccountClient(
    address=account_address,
    net="testnet",
    chain=StarknetChainId.TESTNET,
    key_pair=key_pair,
)
print(acc_client.get_balance_sync())

print(key_pair.public_key)

# identifier_manager = identifier_manager_from_abi(abi)

# print(identifier_manager)
contract_address = "0x0562ef6ba1fd0982a15aa2b00c9ca3774ddcef2e5b8364673b0041d085b37aec"
key = 1234
contract = Contract.from_address_sync(contract_address, acc_client)


call_func = contract.functions["get_trump"].call_sync()

print(call_func)

invocation = contract.functions["leave_game"].invoke_sync(max_fee=5000000000000000000)
invocation.wait_for_acceptance_sync()


print(invocation)

# print(contract.functions)
