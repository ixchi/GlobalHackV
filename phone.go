package main

import (
	"github.com/njern/gonexmo"
	"log"
	"net/http"
	"os"
)

func main() {
	nexmoClient, _ := nexmo.NewClientFromAPI(os.Getenv("NEXMO_KEY"), os.Getenv("NEXMO_SECRET"))
	balance, err := nexmoClient.Account.GetBalance()
	if err != nil {
		log.Fatal(err)
	}
	log.Println(balance)

	messages := make(chan *nexmo.RecvdMessage)
	h := nexmo.NewMessageHandler(messages, false)

	go func() {
		for msg := range messages {
			log.Println(msg)
		}
	}()

	http.HandleFunc("/phone", h)

	http.ListenAndServe(":4836", nil)
}
