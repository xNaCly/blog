---
title: "Handling JSON in Go"
summary: "Guide about working with JSON in go with HTTP server example"
date: 2023-01-27
tags:
  - go
---

Go has a gigantic standard library and of course JSON encoding as well as decoding is included.

## Converting a go struct to a JSON object

We first start of by defining a Go structure as a type and afterwards creating a new variable with an instance of this type...

```go
// main.go
package main

type Car struct {
	Name  string `json:"name"`
	Age   int    `json:"age"`
	Model string `json:"model"`
}

type Person struct {
	Name     string `json:"name"`
	Age      int    `json:"age"`
	Hometown string `json:"home_town"`
	Cars     []Car  `json:"cars"`
}
```

I use a fairly complex data structure here to showcase converting nested structs to json.

{{<callout type="Tip">}}
Notice the raw go strings behind each property?

The text in between the quotation marks tells the json parser / generator which Go structure key has what json object key.

```go
type TestStruct struct {
    TestName string `json:"name"`
}
test := TestStruct{ TestName: "text" }
```

Converting the above to json, yields the result below:

```json
{
  "name": "text"
}
```

{{</callout>}}

To convert structures to json objects we will need the `encoding/json` package imported from the standard library.:

```go {hl_lines=["4-6"]}
// main.go
package main

import (
	"encoding/json"
)

type Car struct {
	Name  string `json:"name"`
	Age   int    `json:"age"`
	Model string `json:"model"`
}

type Person struct {
	Name     string `json:"name"`
	Age      int    `json:"age"`
	Hometown string `json:"home_town"`
	Cars     []Car  `json:"cars"`
}
```

Now we create a new variable of type Person and assign some data to it:

```go {hl_lines=["21-31"]}
// main.go
package main

import (
	"encoding/json"
)

type Car struct {
	Name  string `json:"name"`
	Age   int    `json:"age"`
	Model string `json:"model"`
}

type Person struct {
	Name     string `json:"name"`
	Age      int    `json:"age"`
	Hometown string `json:"home_town"`
	Cars     []Car  `json:"cars"`
}

func main(){
    data := Person{
		Name:     "John",
		Age:      30,
		Hometown: "New York",
		Cars: []Car{
			{Name: "Ford", Age: 2014, Model: "F150"},
			{Name: "Mercedes", Age: 2003, Model: "R class"},
		},
	}
}
```

To convert this `Person` structure to json we call the `json.Marshall` function which returns the converted json as a bytes array and print it as a string:

```go {hl_lines=[32, "34-36", "38"]}
// main.go
package main

import (
	"encoding/json"
)

type Car struct {
	Name  string `json:"name"`
	Age   int    `json:"age"`
	Model string `json:"model"`
}

type Person struct {
	Name     string `json:"name"`
	Age      int    `json:"age"`
	Hometown string `json:"home_town"`
	Cars     []Car  `json:"cars"`
}

func main(){
    data := Person{
		Name:     "John",
		Age:      30,
		Hometown: "New York",
		Cars: []Car{
			{Name: "Ford", Age: 2014, Model: "F150"},
			{Name: "Mercedes", Age: 2003, Model: "R class"},
		},
	}

    res, err := json.Marshal(data)

	if err != nil {
		log.Fatalln("failed to convert struct to json", err)
	}

	log.Println(string(res))
}
```

Of course we need to handle the error `json.Marshal` could return if converting the structure to a json object failed.

Running the above results in the following output:

```text
$ go run .
2023/01/27 13:02:45 {"name":"John","age":30,"home_town":"New York","cars":[{"name":"Ford","age":2014,"model":"F150"},{"name":"Mercedes","age":2003,"model":"R class"}]}
```

The pretty printed json looks like this:

```json
{
  "name": "John",
  "age": 30,
  "home_town": "New York",
  "cars": [
    { "name": "Ford", "age": 2014, "model": "F150" },
    { "name": "Mercedes", "age": 2003, "model": "R class" }
  ]
}
```

## Converting a JSON object to a go struct

To reverse the previously generated json back to a struct we use the `json.Unmarshal` method...

```go {hl_lines=[40, 41, "43-45", 47]}
package main

import (
	"encoding/json"
	"log"
)

type Car struct {
	Name  string `json:"name"`
	Age   int    `json:"age"`
	Model string `json:"model"`
}

type Person struct {
	Name     string `json:"name"`
	Age      int    `json:"age"`
	Hometown string `json:"home_town"`
	Cars     []Car  `json:"cars"`
}

func main() {
	data := Person{
		Name:     "John",
		Age:      30,
		Hometown: "New York",
		Cars: []Car{
			{Name: "Ford", Age: 2014, Model: "F150"},
			{Name: "Mercedes", Age: 2003, Model: "R class"},
		},
	}

	res, err := json.Marshal(data)

	if err != nil {
		log.Fatalln("failed to convert struct to json", err)
	}

	log.Println(string(res))

	newPerson := Person{}
	err = json.Unmarshal(res, &newPerson)

	if err != nil {
		log.Fatalln("failed to convert json back to struct", err)
	}

	log.Println(newPerson)
}
```

To use the unmarshal function we have to pass it a byte array (`res []byte`) as the first parameter and provide a reference to a variable
we want the json to be converted into as the second parameter (`&newPerson &Person`). `json.Unmarshal` can return an error if converting the json to a struct fails. We catch this error just like before.

At the end we print the result. The whole program now prints the following:

```text
$ go run .
2023/01/27 13:14:36 {"name":"John","age":30,"home_town":"New York","cars":[{"name":"Ford","age":2014,"model":"F150"},{"name":"Mercedes","age":2003,"model":"R class"}]}
2023/01/27 13:14:36 {John 30 New York [{Ford 2014 F150} {Mercedes 2003 R class}]}
```

## HTTP server example

The following is a simple http server setup in ~50 lines, which returns the requester a go structure as a JSON string.

```go
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"
)

const PORT = "8080"

// define the data we want to convert to json using the raw strings after the struct fields
type RequestData struct {
	Method      string `json:"method"`
	URL         string `json:"url"`
	RemoteAddr  string `json:"remote_addr"`
	StatusCode  int    `json:"status_code"`
	Status      string `json:"status"`
	RequestTime string `json:"request_time"`
}

func getRoot(w http.ResponseWriter, r *http.Request) {
    // timestamp used for calculating the duration the response took the server to complete
	begin := time.Now()

	log.Printf("[%s] %s %s", r.Method, r.URL.Path, r.RemoteAddr)

    // define variable of type RequestData and fill its fields with data
	data := RequestData{
		Method:      r.Method,
		URL:         r.URL.Path,
		RemoteAddr:  r.RemoteAddr,
		StatusCode:  http.StatusOK,
		Status:      fmt.Sprint(http.StatusOK) + " " + http.StatusText(http.StatusOK),
		RequestTime: fmt.Sprint(time.Since(begin).Milliseconds()) + "ms",
	}

    // convert the above variable to its json representation
	res, err := json.Marshal(data)

    // handle possible errors by returning 500 as a statuscode
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		io.WriteString(w, http.StatusText(http.StatusInternalServerError))
		return
	}

	w.Header().Set("Content-Type", "application/json")
	io.WriteString(w, string(res))
}

func main() {
	http.HandleFunc("/", getRoot)
	log.Println("Listening on port", PORT)
	log.Fatalln(http.ListenAndServe(":"+PORT, nil))
}
```

Calling the above yields the following output:

```text
$ go run .
2023/01/27 13:36:56 Listening on port 8080
2023/01/27 13:37:01 [GET] / 127.0.0.1:51832
```

Curling the endpoints returns the following json:

```text
$ curl -v localhost:8080
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET / HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.87.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Fri, 27 Jan 2023 12:35:33 GMT
< Content-Length: 115
<
* Connection #0 to host localhost left intact
{"method":"GET","url":"/","remote_addr":"127.0.0.1:34920","status_code":200,"status":"200 OK","request_time":"0ms"}
```

The pretty printed json:

```json
{
  "method": "GET",
  "url": "/",
  "remote_addr": "127.0.0.1:34920",
  "status_code": 200,
  "status": "200 OK",
  "request_time": "0ms"
}
```
