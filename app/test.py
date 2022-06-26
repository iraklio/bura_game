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


private_key = 1234512345123451234511111
account_address = (
    2228590030225125150508891573340738205591769373376258767317791333991284410793
)


# # account_address = "0x03e327de1c40540b98d05cbcb13552008e36f0ec8d61d46956d2f9752c294328"

key_pair = KeyPair.from_private_key(private_key)

acc_client = AccountClient(
    address=account_address,
    net="testnet",
    chain=StarknetChainId.TESTNET,
    key_pair=key_pair,
)
print(acc_client.get_balance_sync())


# identifier_manager = identifier_manager_from_abi(abi)

# print(identifier_manager)
contract_address = "0x01336FA7C870A7403ACED14DDA865B75F29113230ED84E3A661F7AF70FE83E7B"
key = 1234
contract = Contract.from_address_sync(contract_address, acc_client)
invocation = contract.functions["set_value"].invoke_sync(
    key, 7, max_fee=500000000000000000000000000
)
invocation.wait_for_acceptance_sync()

# print(contract.functions)
