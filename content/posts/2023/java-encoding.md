---
title: "Handle CSV, JSON and XML with Java"
date: 2023-02-07
summary: "Small guide with snippets for encoding and decoding data into csv, json and xml"
tags:
  - java
---

{{<callout type="Info">}}
In this guide we will parse an array list of hash maps into CSV, JSON and XML. The core concepts can be applied to parsing pretty much anything.
{{</callout>}}

## CSV

Example for data in the CSV format:

```text
name,surname,age
john,doe,45
jan,doe,35
```

Tabular presentation:

| index | name | surname | age |
| ----- | ---- | ------- | --- |
| 0     | john | doe     | 45  |
| 1     | jan  | doe     | 35  |

Parsing values separated by comma is by far the easiest of the three encodings in this guide. Keep the separator in mind (here `,`, but could be any of: `;`, `|`, `:` or `\t`) and check for a header row.

To keep this guide simple we hard-code the header keys and will not parse them dynamically:

### Decoding

To convert a data from CSV to Hash maps in a array list we will first read a file (`data.csv`) with the above content.

```java
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;

public class Main {
    public static void main(String[] args) {
        ArrayList<HashMap<String, String>> result = new ArrayList<>();
        try{
            // open the 'data.csv' file and create a reader
            FileReader fileReader = new FileReader("data.csv");
            // pass the reader to a buffered reader
            BufferedReader bufferedReader = new BufferedReader(fileReader);

            bufferedReader
                // loop over the lines using the .lines() method
                // which returns a stream
                .lines()
                // skip the header line
                .skip(1)
                // iterate over each line
                .forEach(l -> {
                    // allocate a new hash map
                    HashMap<String, String> temp = new HashMap<>();

                    // split the line via its separator
                    String[] splitLine = l.split(",");
                    // assign the values to the know keys
                    temp.put("name", splitLine[0]);
                    temp.put("surname", splitLine[1]);
                    temp.put("age", splitLine[2]);

                    // add the hash map to the result list
                    result.add(temp);
                });
        } catch (Exception e){
            // prints out if file cant be found or read
            e.printStackTrace();
        }

        // print all hash maps in the list
        result.forEach(System.out::println);
    }
}
```

Running the above yields the following result:

```text
{surname=doe, name=john, age=45}
{surname=doe, name=jan, age=35}
```

### Encoding

Encoding to csv is also very simple, instantiate a `StringBuilder`, append the header and after that append each line:

```java {hl_lines=["44-63"]}
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;

public class Main {
    public static void main(String[] args) {
        ArrayList<HashMap<String, String>> result = new ArrayList<>();
        try{
            // open the 'data.csv' file and create a reader
            FileReader fileReader = new FileReader("data.csv");
            // pass the reader to a buffered reader
            BufferedReader bufferedReader = new BufferedReader(fileReader);

            bufferedReader
                // loop over the lines using the .lines() method
                // which returns a stream
                .lines()
                // skip the header line
                .skip(1)
                // iterate over each line
                .forEach(l -> {
                    // allocate a new hash map
                    HashMap<String, String> temp = new HashMap<>();

                    // split the line via its separator
                    String[] splitLine = l.split(",");
                    // assign the values to the know keys
                    temp.put("name", splitLine[0]);
                    temp.put("surname", splitLine[1]);
                    temp.put("age", splitLine[2]);

                    // add the hash map to the result list
                    result.add(temp);
                });
        } catch (Exception e){
            // prints out if the csv is invalid or file cant be found / read
            e.printStackTrace();
        }

        // print all hash maps in the list
        result.forEach(System.out::println);

        StringBuilder stringBuilder = new StringBuilder();

        // append the header row + the line separator of the system
        stringBuilder
            .append("name,surname,age")
            .append(System.lineSeparator());

        // loop over each line
        result.forEach(e -> {
            // create the row by getting the values from the current hash map
            String formattedRow = String.format("%s,%s,%s,%s",
                    e.get("name"),
                    e.get("surname"),
                    e.get("age"),
                    System.lineSeparator());
            // add the new row to the string builder
            stringBuilder.append(formattedRow);
        });

        System.out.println(stringBuilder);
    }
}
```

Running the above yields the following result:

```text
{surname=doe, name=john, age=45}
{surname=doe, name=jan, age=35}
name,surname,age
john,doe,45
jan,doe,35
```

As expected, first the two decoded rows, afterwards the encoded representation as csv with the header row.

## XML

XML is a somewhat outdated data exchange format, but especially people around java use it for configurations and data storage.
The format is a lot more verbose, especially compared to csv.

Example for data in the XML format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <person>
        <name>John</name>
        <surname>Doe</surname>
        <age>45</age>
    </person>
    <person>
        <name>Jan</name>
        <surname>Doe</surname>
        <age>35</age>
    </person>
</root>
```

### Decoding

Parsing XML requires a lot of boilerplate in Java so be prepared. I copied the above XML to a `data.xml` file.

```java
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.util.ArrayList;
import java.util.HashMap;

public class Main {
    public static void main(String[] args) {
        // result list which contains all parsed rows
        ArrayList<HashMap<String, String>> result = new ArrayList<>();
        try {
            // create a factory
            DocumentBuilderFactory documentBuilderFactory = DocumentBuilderFactory.newInstance();
            // use the above factory to get a document builder
            DocumentBuilder documentBuilder = documentBuilderFactory.newDocumentBuilder();
            // use the document builder to parse the xml in the file 'data.xml'
            Document doc = documentBuilder.parse("data.xml");

            // get the list of persons
            NodeList personList = doc.getElementsByTagName("person");
            // loop over the list of person
            for (int i = 0; i < personList.getLength(); i++) {
                // create a node out of the current item
                Node item = personList.item(i);
                // check if the node is an Element
                if (item.getNodeType() == Node.ELEMENT_NODE) {
                    // new hash map to contain the values of the row
                    HashMap<String, String> temp = new HashMap<>();
                    // put all values for the keys into the above map
                    temp.put("name", ((Element) item)
                        .getElementsByTagName("name")
                        .item(0)
                        .getTextContent());

                    temp.put("surname", ((Element) item)
                        .getElementsByTagName("surname")
                        .item(0)
                        .getTextContent());

                    temp.put("age", ((Element) item)
                        .getElementsByTagName("age")
                        .item(0)
                        .getTextContent());

                    // add the row to the result list
                    result.add(tmap);
                }
           }
        } catch (Exception e) {
            // triggers if xml is invalid or the file cant be opened
            e.printStackTrace();
        }
        // print the list
        result.forEach(System.out::println);
    }
}
```

Running the above yields the following result:

```text
{surname=Doe, name=John, age=45}
{surname=Doe, name=Jan, age=35}
```

### Encoding

Converting the parsed data back into XML requires even more boilerplate so read the comments carefully:

```java {hl_lines=["8-13", "66-123"]}
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.HashMap;

public class XML {
    public static void main(String[] args) {
        // result list which contains all parsed rows
        ArrayList<HashMap<String, String>> result = new ArrayList<>();
        try {
            // create a factory
            DocumentBuilderFactory documentBuilderFactory = DocumentBuilderFactory.newInstance();
            // use the above factory to get a document builder
            DocumentBuilder documentBuilder = documentBuilderFactory.newDocumentBuilder();
            // use the document builder to parse the xml in the file 'data.xml'
            Document doc = documentBuilder.parse("data.xml");

            // get the list of persons
            NodeList personList = doc.getElementsByTagName("person");
            // loop over the list of person
            for (int i = 0; i < personList.getLength(); i++) {
                // create a node out of the current item
                Node item = personList.item(i);
                // check if the node is an Element
                if (item.getNodeType() == Node.ELEMENT_NODE) {
                    // new hash map to contain the values of the row
                    HashMap<String, String> temp = new HashMap<>();
                    // put all values for the keys into the above map
                    temp.put("name", ((Element) item)
                        .getElementsByTagName("name")
                        .item(0)
                        .getTextContent());

                    temp.put("surname", ((Element) item)
                        .getElementsByTagName("surname")
                        .item(0)
                        .getTextContent());

                    temp.put("age", ((Element) item)
                        .getElementsByTagName("age")
                        .item(0)
                        .getTextContent());

                    // add the row to the result list
                    result.add(tmap);
                }
           }
        } catch (Exception e) {
            // triggers if xml is invalid or the file cant be opened
            e.printStackTrace();
        }
        // print the list
        result.forEach(System.out::println);

        try {
            // create a factory
            DocumentBuilderFactory documentBuilderFactory = DocumentBuilderFactory.newInstance();
            // use the factory to get a new document builder
            DocumentBuilder documentBuilder = documentBuilderFactory.newDocumentBuilder();

            // use the document builder to get a new document
            Document doc = documentBuilder.newDocument();

            // create the root element
            Element rootElement = doc.createElement("root");
            // append the root element to the document
            doc.appendChild(rootElement);

            // loop over the maps in the result list
            for (HashMap<String, String> map : result) {
                // create a person element
                Element person = doc.createElement("person");
                // add the person element to the root element
                rootElement.appendChild(person);

                // create elements and set their text content
                // to the value stored in the hash map
                Element name = doc.createElement("name");
                name.setTextContent(map.get("name"));
                person.appendChild(name);

                Element surname = doc.createElement("surname");
                surname.setTextContent(map.get("surname"));
                person.appendChild(surname);

                Element age = doc.createElement("age");
                age.setTextContent(map.get("age"));
                person.appendChild(age);
            }

            // get a new transformer factory
            TransformerFactory transformerFactory = TransformerFactory.newInstance();
            // use the factory to get a new Transformer
            Transformer transformer = transformerFactory.newTransformer();

            // instruct the transformer
            // to add XML declaration at the top of the file
            transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");
            // instruct the transformer to indent the output
            transformer.setOutputProperty(OutputKeys.INDENT, "yes");

            // get a new DOMSource from the document
            DOMSource source = new DOMSource(doc);
            // create a stringwriter to transform the source into
            StringWriter stringWriter = new StringWriter();
            transformer.transform(source, new StreamResult(stringWriter));

            // print the output
            System.out.println(stringWriter);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

Running the above yields the following result:

```text
{surname=Doe, name=John, age=45}
{surname=Doe, name=Jan, age=35}
<root>
    <person>
        <name>John</name>
        <surname>Doe</surname>
        <age>45</age>
    </person>
    <person>
        <name>Jan</name>
        <surname>Doe</surname>
        <age>35</age>
    </person>
</root>
```

## JSON

Json is the de facto standard data exchange and configuration standard. The whole JavaScript and Typescript ecosystem uses JSON to configure tools and send + receive data from REST APIS.

{{<callout type="Danger">}}
To parse json we us the [org.json](https://github.com/stleary/JSON-java) library. I wont discuss package / library managment in depth here, but the repo includes a guide for adding the library to your project.

#### Adding org.json to your project using gradle:

- Add the following highlighted line to your `build.gradle`:

```gradle {hl_lines=[13]}
plugins {
    id 'java'
}

group 'org.example'
version null

repositories {
    mavenCentral()
}

dependencies {
    implementation group: 'org.json', name: 'json', version: '20211205'
}
```

- Click on the green arrow next to the `dependencies` to download the dependency

{{</callout>}}

### Decoding

The example we want to parse into an `ArrayList` of hash maps is the following:

```json
[
  {
    "name": "John",
    "surname": "Doe",
    "age": 45
  },
  {
    "name": "Jan",
    "surname": "Doe",
    "age": 35
  }
]
```

Parsing a string to json is fairly easy while using the org.json library:

```java
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.stream.Collectors;

import org.json.*;

public class Main {
    public static void main(String[] args) {
        ArrayList<HashMap<String, String>> result = new ArrayList<>();
        try{
            // create a new file
            File file = new File("data.json");
            FileReader fileReader = new FileReader(file);
            // read file with bufferedReader for better perf
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            // read the lines and join them by "\n"
            String fileContent = bufferedReader.lines().collect(Collectors.joining("\n"));

            // use org.json.JSONArray to parse the string to a json object
            JSONArray jsonArray = new JSONArray(fileContent);
            // loop over every object in the array
            for(int i = 0; i < jsonArray.length(); i++){
                // create a new json object for every entry in the array
                JSONObject o = jsonArray.getJSONObject(i);

                // hash map to store row values
                HashMap<String, String> temp = new HashMap<>();
                // add values to keys
                temp.put("name", o.getString("name"));
                temp.put("surname", o.getString("surname"));
                temp.put("age", String.valueOf(o.getInt("age")));

                // add row to result
                result.add(temp);
            }
        } catch (Exception e){
            e.printStackTrace();
        }

        result.forEach(System.out::println);
    }
}
```

The above results in the same output as the parsing for CSV and XML:

```text
{surname=Doe, name=John, age=45}
{surname=Doe, name=Jan, age=35}
```

### Encoding

Encoding java objects into json is so easy it can be done in one loc:

```java {hl_lines=[47]}
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.stream.Collectors;

import org.json.*;

public class Main {
    public static void main(String[] args) {
        ArrayList<HashMap<String, String>> result = new ArrayList<>();
        try{
            // create a new file
            File file = new File("data.json");
            FileReader fileReader = new FileReader(file);
            // read file with bufferedReader for better perf
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            // read the lines and join them by "\n"
            String fileContent = bufferedReader
                .lines()
                .collect(Collectors.joining("\n"));

            // use org.json.JSONArray to parse the string to a json object
            JSONArray jsonArray = new JSONArray(fileContent);
            // loop over every object in the array
            for(int i = 0; i < jsonArray.length(); i++){
                // create a new json object for every entry in the array
                JSONObject o = jsonArray.getJSONObject(i);

                // hash map to store row values
                HashMap<String, String> temp = new HashMap<>();
                // add values to keys
                temp.put("name", o.getString("name"));
                temp.put("surname", o.getString("surname"));
                temp.put("age", String.valueOf(o.getInt("age")));

                // add row to result
                result.add(temp);
            }
        } catch (Exception e){
            e.printStackTrace();
        }

        result.forEach(System.out::println);

        System.out.println(new JSONArray(result).toString(4));
    }
}
```

The above results in:

```text
{surname=Doe, name=John, age=45}
{surname=Doe, name=Jan, age=35}
[
    {
        "name": "John",
        "surname": "Doe",
        "age": "45"
    },
    {
        "name": "Jan",
        "surname": "Doe",
        "age": "35"
    }
]
```
