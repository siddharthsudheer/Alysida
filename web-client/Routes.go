package main

import "net/http"

type Route struct {
	Name        string
	Method      string
	Pattern     string
	HandlerFunc http.HandlerFunc
}

type Routes []Route

var routes = Routes{
	Route{
		"Index",
		"GET",
		"/",
		Index,
	},
	Route{
		"MyPeers",
		"GET",
		"/my-peers",
		MyPeers,
	},
	Route{
		"AddPeers",
		"GET",
		"/add-peers",
		AddPeers,
	},
	Route{
		"AddPeers",
		"POST",
		"/add-peers",
		AddPeers,
	},
	Route{
		"RegisterMe",
		"GET",
		"/register-me",
		RegisterMe,
	},
	Route{
		"UnconfirmedTxns",
		"GET",
		"/unconfirmed-txns",
		UnconfirmedTxns,
	},
	Route{
		"AddTxn",
		"GET",
		"/add-txn",
		AddTxn,
	},
	Route{
		"AddTxn",
		"POST",
		"/add-txn",
		AddTxn,
	},
}
