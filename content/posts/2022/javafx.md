---
title: "Custom events and submitting on enter using JavaFx"
summary: Creating custom events in javafx to handle submitting on enter in TextFields
date: 2022-07-14
slug: javafx-events
tags: 
- java
- javafx
---

This blog post will showcase a simple, small and often overlooked usage of event handlers[^1] in Javafx[^2].

First we start off by creating a new JavaFx app named `Demo` extending `Application` with an attribute `s` of type
`Scene`. Our class also includes the standard main method calling the launch method inherited from the `Application`
class.

```java
import javafx.application.Application;
import javafx.scene.Scene;

public class Demo extends Application {
    Scene s;

    public static void main(String[] args) {
        launch(args);
    }
}
```

Our next step is to create a new Scene and add both a `TextField` and a `Button` to a vertical aligned box (`VBox`).
This can be archived by adding the following code to a new method called `start` and creating a new method called
`createContent`:

```java
/**/
import javafx.scene.control.Button;
import javafx.scene.control.TextField;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import javafx.scene.Parent;


public class Demo extends Application {
    /**/

    private Parent createContent() {
        Button b = new Button("Submit");
        TextField tf = new TextField("Placeholder");
        tf.setId("textarea-main");

        return new VBox(tf, b);
    }

    @Override
    public void start(Stage primaryStage) {
        this.s = new Scene(createContent(), 500, 500);
        primaryStage.setScene(this.s);
        primaryStage.show();
    }

    /**/
}
```

Your Application should now look like this:

![image](/javafx/javafxdemo.webp)

The next move is to implement our custom event which will fire on pressing `Enter`:

```java
/**/
import javafx.event.Event;
import javafx.event.EventType;

class UserEvent extends Event {
    public static final EventType<UserEvent> _KEY_ENTER = new EventType<>(ANY, "_KEY_ENTER");
    public UserEvent(EventType<? extends Event> eventType){
        super(eventType);
    }
}

public class Demo extends Application {
  /**/
}
```

Now we can implement the `event_handler` method:

```java
/**/

/**/

public class Demo extends Application {
    /**/

    private void event_handler(Event e) {
        TextField t = (TextField) this.s.lookup("#textarea-main");
        switch (e.getEventType().getName()) {
            case "_KEY_ENTER":
            case "MOUSE_PRESSED": {
                System.out.println(t.getText().trim());
                break;
            }
            default:
                System.out.println("Unknown Event");
        }
    }

    /**/

    /**/
}
```

This should log the content of the `TextField` on pressing `Enter` or clicking on the `Submit`-Button once we implement
firing these events in the following snippet by adding an ID to the `TextField` which we will use to query the `Scene`
to look for the `TextField` and extract its content. We will also add two event listeners, the first on the Button and
the second on the `TextField`:

```java
/**/

/**/

public class Demo extends Application {
  /**/

  private Parent createContent() {
        Button b = new Button("Submit");
        b.addEventHandler(UserEvent._KEY_ENTER, this::event_handler);
        b.setOnMousePressed(this::event_handler);

        TextField tf = new TextField("Placeholder");
        tf.setId("textarea-main");
        tf.setOnKeyPressed(k -> {
            if(k.getCode() == KeyCode.ENTER) b.fireEvent(new UserEvent(UserEvent._KEY_ENTER));
        });

        return new VBox(tf, b);
    }

    /**/

    /**/

    /**/
}
```

The `TextField` now fires a event of type `_KEY_ENTER` which we are listening for in `Demo.event_handler()`. Clicking
the Button fires an `MOUSE_PRESSED` and the `_KEY_ENTER` event which will also be processed by our event handling.

```java
b.addEventHandler(UserEvent._KEY_ENTER, this::event_handler);
b.setOnMousePressed(this::event_handler);
tf.setOnKeyPressed(/**/);
```

After putting everything together, the app should look like this:

![image](/javafx/result.webp)

Congrats, you implemented submitting on enter :)

Full code:

```java
import javafx.application.Application;
import javafx.event.Event;
import javafx.event.EventType;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.TextField;
import javafx.scene.input.KeyCode;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

class UserEvent extends Event {
    public static final EventType<UserEvent> _KEY_ENTER = new EventType<>(ANY, "_KEY_ENTER");
    public UserEvent(EventType<? extends Event> eventType){
        super(eventType);
    }
}

public class Demo extends Application {
    Scene s;


    private Parent createContent() {
        Button b = new Button("Submit");
        b.addEventHandler(UserEvent._KEY_ENTER, this::event_handler);
        b.setOnMousePressed(this::event_handler);

        TextField tf = new TextField("Placeholder");
        tf.setId("textarea-main");
        tf.setOnKeyPressed(k -> {
            if(k.getCode() == KeyCode.ENTER) b.fireEvent(new UserEvent(UserEvent._KEY_ENTER));
        });

        return new VBox(tf, b);
    }

    private void event_handler(Event e) {
        TextField t = (TextField) this.s.lookup("#textarea-main");
        switch (e.getEventType().getName()) {
            case "_KEY_ENTER":
            case "MOUSE_PRESSED": {
                System.out.println(t.getText().trim());
                break;
            }
            default:
                System.out.println("Unknown Event");
        }
    }

    @Override
    public void start(Stage primaryStage) {
        this.s = new Scene(createContent(), 500, 500);
        primaryStage.setScene(this.s);
        primaryStage.setTitle("Demo");
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
```

[^1]: https://fxdocs.github.io/docs/html5/#_event_handling
[^2]: https://openjfx.io/
