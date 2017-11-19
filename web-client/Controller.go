package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
)

/*
	Page that shows the whole blockchain
	and allows user register their node,
	if not registered
*/
func Index(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=UTF-8")
	w.WriteHeader(http.StatusOK)

	HomePageVars := HomePageVariables{
		AlysidaAddr:   flags["alysidaAddr"],
		WebClientAddr: fmt.Sprintf("http://localhost%s", flags["clientPort"]),
	}

	t, err := template.ParseFiles("pages/homepage.html")
	checkErr(err)
	err = t.Execute(w, HomePageVars)
	checkErr(err)
}

/*
	Page that shows currently registered peers
*/
func MyPeers(w http.ResponseWriter, r *http.Request) {
	var p PeerList
	url := fmt.Sprintf("%s/get-peer-addresses", flags["alysidaAddr"])

	response, err := http.Get(url)
	checkErr(err)

	defer response.Body.Close()
	body, err := ioutil.ReadAll(response.Body)
	checkErr(err)

	jsonErr := json.Unmarshal(body, &p)
	checkErr(jsonErr)

	w.Header().Set("Content-Type", "text/html; charset=UTF-8")
	w.WriteHeader(http.StatusOK)

	t, err := template.ParseFiles("pages/my-peers.html")
	checkErr(err)
	err = t.Execute(w, p)
	checkErr(err)
}

/*
	Page that allows user to add peer
	IP addresses
*/
func AddPeers(w http.ResponseWriter, r *http.Request) {
	if r.Method == "GET" {
		w.Header().Set("Content-Type", "text/html; charset=UTF-8")
		w.WriteHeader(http.StatusOK)

		t, err := template.ParseFiles("pages/add-peers.html")
		checkErr(err)
		err = t.Execute(w, nil)
		checkErr(err)
	} else {
		r.ParseForm()
		ipsStr := strings.Trim(strings.Replace(string(r.Form["add_new_peers"][0]), " ", "", -1), ";")
		ipAddresses := strings.Split(ipsStr, ";")

		requestURL := fmt.Sprintf("%s/add-peer-addresses", flags["alysidaAddr"])
		u := IpAddrs{Ips: ipAddresses}
		b := new(bytes.Buffer)
		json.NewEncoder(b).Encode(u)
		res, _ := http.Post(requestURL, "application/json; charset=utf-8", b)
		io.Copy(os.Stdout, res.Body)
		http.Redirect(w, r, "/my-peers", http.StatusMovedPermanently)
	}
}

/*
	Page that allows user to add peer
	IP addresses
*/
func RegisterMe(w http.ResponseWriter, r *http.Request) {
	var reg []RegistrationResponse
	url := fmt.Sprintf("%s/register-me", flags["alysidaAddr"])

	response, err := http.Get(url)
	checkErr(err)

	defer response.Body.Close()
	body, err := ioutil.ReadAll(response.Body)
	checkErr(err)

	jsonErr := json.Unmarshal(body, &reg)
	checkErr(jsonErr)

	w.Header().Set("Content-Type", "text/html; charset=UTF-8")
	w.WriteHeader(http.StatusOK)

	t, err := template.ParseFiles("pages/registration-response.html")
	checkErr(err)
	err = t.Execute(w, reg)
	checkErr(err)
}

/*
	Page that shows current Unconfirmed Transactions
*/
func UnconfirmedTxns(w http.ResponseWriter, r *http.Request) {
	var u TransactionList
	url := fmt.Sprintf("%s/get-unconfirmed-transactions", flags["alysidaAddr"])

	response, err := http.Get(url)
	checkErr(err)

	defer response.Body.Close()
	body, err := ioutil.ReadAll(response.Body)
	checkErr(err)

	jsonErr := json.Unmarshal(body, &u)
	checkErr(jsonErr)

	w.Header().Set("Content-Type", "text/html; charset=UTF-8")
	w.WriteHeader(http.StatusOK)

	t, err := template.ParseFiles("pages/unconfirmed-txns.html")
	checkErr(err)
	err = t.Execute(w, u)
	checkErr(err)
}

/*
	Page that allows user to add new
	transactions
*/
func AddTxn(w http.ResponseWriter, r *http.Request) {
	if r.Method == "GET" {
		w.Header().Set("Content-Type", "text/html; charset=UTF-8")
		w.WriteHeader(http.StatusOK)

		t, err := template.ParseFiles("pages/add-txn.html")
		checkErr(err)
		err = t.Execute(w, nil)
		checkErr(err)
	} else {
		r.ParseForm()

		requestURL := fmt.Sprintf("%s/add-new-transaction", flags["alysidaAddr"])
		u := TransactionData{
			Sender:   fmt.Sprintf("%s", r.Form["sender"][0]),
			Receiver: fmt.Sprintf("%s", r.Form["receiver"][0]),
			Amount:   fmt.Sprintf("%s", r.Form["amount"][0]),
		}
		b := new(bytes.Buffer)
		json.NewEncoder(b).Encode(u)
		res, _ := http.Post(requestURL, "application/json; charset=utf-8", b)
		io.Copy(os.Stdout, res.Body)
		http.Redirect(w, r, "/unconfirmed-txns", http.StatusMovedPermanently)
	}
}
