package main

import (
    "fmt"
    "image"
    "log"
    "os"
    _ "image/jpeg"
)

func main() {

    reader, err := os.Open("pieces/four-pieces.jpg")
    if err != nil {
        log.Fatal(err)
    }
    defer reader.Close()

    m, _, err := image.Decode(reader)
    if err != nil {
        log.Fatal(err)
    }
    bounds := m.Bounds()

    fmt.Println(bounds)
}
