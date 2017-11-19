package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
)

var flags map[string]string

func init() {
	alysidaPort := flag.Int("alysida-port", 4200, "Alysída Port Number")
	webClientPort := flag.Int("client-port", 5200, "Web Client Port Number")
	flag.Parse()

	flags = make(map[string]string)
	flags["alysidaAddr"] = fmt.Sprintf("http://localhost:%d", *alysidaPort)
	flags["clientPort"] = fmt.Sprintf(":%d", *webClientPort)
}

func main() {
	router := NewRouter()

	//Static Resources
	router.PathPrefix("/static").Handler(http.StripPrefix("/static", http.FileServer(http.Dir("./static"))))

	log.Fatal(http.ListenAndServe(flags["clientPort"], router))
}

func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
