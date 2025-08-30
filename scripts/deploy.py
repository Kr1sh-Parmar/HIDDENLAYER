from brownie import GreenHydrogenCredit, accounts, network
import os

def main():
    """
    Deploys the GreenHydrogenCredit smart contract.
    This script is run via `brownie run scripts/deploy.py`.
    """
    print(f"Active network is {network.show_active()}")
    
    # Use the first account provided by the local network as the 'government'.
    # For testnets, you would load an account from your encrypted keystore.
    gov_account = accounts[0]
    
    print(f"Deployer (Government) Account: {gov_account.address}")
    print("Deploying contract...")

    # Deploy the contract. The '{'from': gov_account}' argument sets the deployer
    # and therefore the contract's "Owner".
    credit_contract = GreenHydrogenCredit.deploy({'from': gov_account})
    
    print(f"SUCCESS: Contract deployed at address: {credit_contract.address}")
    print("You can now interact with it using the Brownie console or your web app.")
    
    return credit_contract