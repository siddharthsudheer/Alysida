package main

/*
	Variables for Hompage
*/
type HomePageVariables struct {
	AlysidaAddr   string
	WebClientAddr string
}

/*
	Variables for My Peers Page
*/
type PeerList struct {
	Peers []string `json:"peers"`
}

/*
	Type Struct to allow
	user to POST new
	IP Addresses
*/
type IpAddrs struct {
	Ips []string `json:"ips"`
}

type RegistrationPeerResponse struct {
	Title   string `json:"title"`
	Message string `json:"message"`
}

type RegistrationResponse struct {
	Peer     string                   `json:"peer"`
	Response RegistrationPeerResponse `json:"response"`
}

type Transaction struct {
	Hash      string `json:"hash"`
	TxnData   string `json:"txn_data"`
	TimeStamp string `json:"time_stamp"`
}

type TransactionList struct {
	UnconfirmedTxns []Transaction `json:"unconfirmed_txns"`
}

type TransactionData struct {
	Sender   string `json:"sender"`
	Receiver string `json:"receiver"`
	Amount   string `json:"amount"`
}
