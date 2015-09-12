package main

import (
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.GET("/message", func(c *gin.Context) {

	})

	r.Run(":8038")
}
