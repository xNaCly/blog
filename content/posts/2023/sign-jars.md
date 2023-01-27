---
title: "How to sign jar files"
summary: "Guide for signing jar files and verifying a jar files signature programmatically"
date: 2023-01-27T15:35:54+01:00
tags:
  - java
---

{{<callout type="Danger">}}
I encountered the error of the `jarsigner` missing from my path.
This error occurs if the `jre` is installed not the `jdk`.
To fix this, install the jdk and set it as your default.

On Arch linux:

```bash
pacman -S jdk-openjdk
archlinux-java set java-19-openjdk
```

You should now be able to run the `jarsigner` and the `keytool`.
{{</callout>}}

## Generating the keystore

{{<callout type="Warning">}}
Make sure your jar is built and in the `jar/` directory.
{{</callout>}}

To generate the keystore run the following command in the parent directory to the `jar/` directory:

```bash
# unix
keytool -genkey -alias server -keyalg RSA -keysize 2048 -keystore keystore.jks
# windows
# change the version to the jdk you're using
"C:\Program Files\Java\jdk-17.0.5\bin\keytool" -genkey -alias server -keyalg RSA -keysize 2048 -keystore keystore.jks
```

Enter the required data.
![keystore output](/sign-jar/keystore.png)
Now check if the key was generated correctly using the following command:

```bash
# unix
keytool -v -list -keystore keystore.jks
# windows
# change the version to the jdk you're using
"C:\Program Files\Java\jdk-17.0.5\bin\keytool" -v -list -keystore keystore.jks
```

![keystore view](/sign-jar/keystore-view.png)

## Signing the jar

After having generated the keystore and viewed if it contains our certificate we are now good to go for signing our jar.

Run the following commands to first sign the jar and afterwards verify the certificate:

{{<callout type="Warning">}}
Replace `<yourpassword>` and `<yourjar>.jar` with the password you choose while generating the keystore and the name of the jar you want to sign.
{{</callout>}}

```bash
# unix
jarsigner -keystore keystore.jks -storepass <password> ./jar/<yourjar>.jar server
jarsigner -verify -keystore keystore.jks -storepass <password> jar\<yourjar>.jar server

# windows
# change the version to the jdk you're using
"C:\Program Files\Java\jdk-17.0.5\bin\jarsigner" -keystore keystore.jks -storepass <password> ./jar/<yourjar>.jar server
"C:\Program Files\Java\jdk-17.0.5\bin\jarsigner" -verify -keystore keystore.jks -storepass <password> jar\<yourjar>.jar server
```

## Verify certificate programmatically

Per convention you should use a factory to build a component which was loaded from a jar.
To verify if the component is signed before loading it into the program insert the following function in your factory and call it before loading the component in your application.

```java
public class ExampleFactory {
    public static boolean verify(String pathToJar){
        String curOs = System.getProperty("os.name");
        boolean isVerified = false;

        ProcessBuilder pb = null;

        // call the jarsigner depending on the operating system
        if(curOs.startsWith("Linux")){
            pb = new ProcessBuilder("jarsigner", "-verify", pathToJar);
        } else if(curOs.startsWith("Windows")){
            pb = new ProcessBuilder("C:\\Program Files\\Java\\jdk-17.0.5\\bin\\jarsigner", "-verify", pathToJar);
        } else {
            return isVerified;
        }

        // go through the output of the jarsigner command and return true if the "verify" is in any of the lines
        try {
            Process p = pb.start();
            InputStream iS = p.getInputStream();
            InputStreamReader iSR = new InputStreamReader(iS);
            BufferedReader bR = new BufferedReader(iSR);

            String line;
            while((line = bR.readLine()) != null){
                if (line.contains("verified")){
                    isVerified = true;
                }
            }
        } catch(Exception e){
            e.printStackTrace();
            return isVerified;
        }

        return isVerified;
    }
}
```
