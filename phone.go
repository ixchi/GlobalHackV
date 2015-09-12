package main

import (
	"github.com/njern/gonexmo"
	"log"
	"net/http"
	"os"
	"strings"
)

var data map[string]map[string]interface{}

func parseMessage(text string) (string, bool) {
	parts := strings.Split(text, "\n")
	if len(parts) != 3 {
		return "Not enough lines! Please include your last name, birth date (YYYY-MM-DD), and driver's license ID.", false
	}

	return "", true
}

func main() {
	data = make(map[string]map[string]interface{})

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
			nexmoClient.SMS.Send(&nexmo.SMSMessage{
				From:  "13374192686",
				To:    msg.MSISDN,
				Type:  nexmo.Text,
				Text:  "Hello! :)",
				Class: nexmo.Standard,
			})
		}
	}()

	http.HandleFunc("/phone", h)

	http.ListenAndServe(":4836", nil)
}
