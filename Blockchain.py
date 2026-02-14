from web3 import Web3
from eth_account import Account
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
import config

class BlockchainManager:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(config.WEB3_PROVIDER_URL))
        self.contract_address = config.CONTRACT_ADDRESS
        self.private_key = config.PRIVATE_KEY
        
        # Load contract ABI
        self.contract_abi = [
            {
                "inputs": [],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "user", "type": "address"},
                    {"internalType": "uint256", "name": "validUntil", "type": "uint256"}
                ],
                "name": "grantAccess",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "user", "type": "address"}
                ],
                "name": "hasValidAccess",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "user", "type": "address"}
                ],
                "name": "getAccessExpiry",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        if self.contract_address and self.private_key:
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=self.contract_abi
            )
            self.account = Account.from_key(self.private_key)
        else:
            self.contract = None
            self.account = None
    
    def mint_access_token(self, user_address: str) -> Dict:
        """Mint time-bound access token"""
        if not self.contract or not self.account:
            return {
                "success": False,
                "error": "Blockchain not configured",
                "mock_token": self._generate_mock_token(user_address)
            }
        
        try:
            # Calculate expiry timestamp
            expiry = int((datetime.utcnow() + timedelta(seconds=config.TOKEN_VALIDITY_SECONDS)).timestamp())
            
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            txn = self.contract.functions.grantAccess(
                Web3.to_checksum_address(user_address),
                expiry
            ).build_transaction({
                'chainId': config.CHAIN_ID,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "success": True,
                "transaction_hash": tx_hash.hex(),
                "user_address": user_address,
                "expiry_timestamp": expiry,
                "expiry_datetime": datetime.fromtimestamp(expiry).isoformat(),
                "block_number": tx_receipt['blockNumber']
            }
        
        except Exception as e:
            print(f"Blockchain error: {e}")
            return {
                "success": False,
                "error": str(e),
                "mock_token": self._generate_mock_token(user_address)
            }
    
    def _generate_mock_token(self, user_address: str) -> Dict:
        """Generate mock token for development"""
        expiry = datetime.utcnow() + timedelta(seconds=config.TOKEN_VALIDITY_SECONDS)
        
        return {
            "token_id": f"MOCK-{user_address[:10]}",
            "user_address": user_address,
            "expiry_timestamp": int(expiry.timestamp()),
            "expiry_datetime": expiry.isoformat(),
            "valid_for_seconds": config.TOKEN_VALIDITY_SECONDS
        }

blockchain_manager = BlockchainManager()
