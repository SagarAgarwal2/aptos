import streamlit as st
import json
import requests
from typing import Optional

class PetraWallet:
    def __init__(self):
        self.connected = False
        self.address = None
        self.network = None

    def connect(self) -> bool:
        """Connect to Petra Wallet"""
        try:
            # This will be handled by the frontend JavaScript
            st.session_state.petra_connected = True
            return True
        except Exception as e:
            st.error(f"Failed to connect to Petra Wallet: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from Petra Wallet"""
        st.session_state.petra_connected = False
        st.session_state.petra_address = None
        st.session_state.petra_network = None

    def is_connected(self) -> bool:
        """Check if wallet is connected"""
        return st.session_state.get('petra_connected', False)

    def get_address(self) -> Optional[str]:
        """Get connected wallet address"""
        return st.session_state.get('petra_address')

    def get_network(self) -> Optional[str]:
        """Get connected network"""
        return st.session_state.get('petra_network')

    def get_wallet_info(self) -> dict:
        """Get wallet information"""
        return {
            'address': st.session_state.get('petra_address'),
            'network': st.session_state.get('petra_network'),
            'public_key': st.session_state.get('petra_public_key'),
            'signature': st.session_state.get('petra_signature'),
            'message': st.session_state.get('petra_message')
        }

    def sign_and_submit_transaction(self, transaction: dict) -> bool:
        """Sign and submit a transaction using Petra Wallet"""
        try:
            # This will be handled by the frontend JavaScript
            st.session_state.last_transaction = transaction
            return True
        except Exception as e:
            st.error(f"Failed to submit transaction: {str(e)}")
            return False 