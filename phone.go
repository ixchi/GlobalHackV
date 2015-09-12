package main

import (
	"github.com/njern/gonexmo"
	"log"
	"net/http"
)

func main() {
	messages := make(chan *nexmo.RecvdMessage)
	h := nexmo.NewMessageHandler(messages, false)

	go func() {
		for {
			msg := <-messages
			log.Printf("%v\n", msg)
		}
	}()

	http.HandleFunc("/phone", h)

	http.ListenAndServe(":4836", nil)
}
