---
title: "Handrolling ISO8601 Duration Support for Go"
summary: "So I need to use ISO8601 durations which Go doesn't support"
date: 2025-07-27
math: true
tags:
  - go
---

{{<callout type="Info - TLDR">}}
I wrote my own ISO8601 duration parsing library because the common ones sucked.
ISO8601 durations are defined as `P[nn]Y[nn]M[nn]DT[nn]H[nn]M[nn]S` or
`P[nn]W`.

See:

- [wikipedia](https://en.wikipedia.org/wiki/ISO_8601#Durations)
- [library](https://github.com/xnacly/go-iso8601-duration)

{{</callout>}}

I'm currently working on a project that requires interacting with the api of a
german public transport provider, specifically _vbb_. To abstract this I wrote
[go-hafas](https://github.com/xnacly/go-hafas), however, all fields that
include `duration` are serialized to something along the lines of `PT3M`, for
instance:

```jsonc
{
  // ...

  // means something like between two stops you require at least this amount
  // to successfully walk from the previous arrival to the next departure
  "minimumChangeDuration": "PT2M",
  // ...
}
```

To use these durations for something like UI, sorting, or internal logic, I
need to parse them into something Go native.

# No Support In Go's Stdlib

I thought, sure, I'll just use
[`time.Duration`](https://pkg.go.dev/time#Duration) and parse the format via
`time.ParseDuration`, until I found out:

1. There is no ISO8601 support in either `time.Parse` (there is support for an
   ISO8601 subset: `time.RFC3339`, just not for a duration) or `time.DurationParse`, which only accepts
   "custom" duration strings someone at google came up with I guess

   ```go
   // ParseDuration parses a duration string.
   // A duration string is a possibly signed sequence of
   // decimal numbers, each with optional fraction and a unit suffix,
   // such as "300ms", "-1.5h" or "2h45m".
   // Valid time units are "ns", "us" (or "µs"), "ms", "s", "m", "h".
   func ParseDuration(s string) (Duration, error) {
   ```

2. `time.Duration` is only backed internally by a `int64`, this doesn't mean it
   can't contain the ISO8601 duration spec, just fun to know

   ```go
   // A Duration represents the elapsed time between two instants
   // as an int64 nanosecond count. The representation limits the
   // largest representable duration to approximately 290 years.
   type Duration int64
   ```

# No "well done" library

So I went looking for a library, which left me dumbfounded, because none of
them supported my obvious use case (converting a ISO8601 duration to
`time.Duration`) and some weren't even spec compliant (see next chapter):

| Library                                                       | Why I didnt chose it                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`dacut/go-iso8601`](https://github.com/dacut/go-iso8601)     | No Duration support                                                                                                                                                                                                                                                         |
| [`relvacode/iso8601`](https://github.com/relvacode/iso8601/)  | No Duration support                                                                                                                                                                                                                                                         |
| [`sosodev/duration`](https://github.com/sosodev/duration)     | [Accepts faulty inputs](https://github.com/sosodev/duration/issues/35), [doesn't treat `W`](https://github.com/sosodev/duration/blob/main/duration.go#L259-L261) [as exclusive](https://github.com/sosodev/duration/blob/main/duration.go#L98-L107)                         |
| [`senseyeio/duration`](https://github.com/senseyeio/duration) | [Uses regex](https://github.com/senseyeio/duration/blob/master/duration.go#L28) (preference), [Doesn't treat `W`](https://github.com/senseyeio/duration/blob/master/duration.go#L56-L57) [as exclusive](https://github.com/senseyeio/duration/blob/master/duration.go#L109) |

So I, as every sensible software developer would, started to write my own
library: [go-iso8601-duration](https://github.com/xnacly/go-iso8601-duration).

# Finding the Specification

This is the part where I was severly pissed off. First of all, I understand why
the go stdlib only supports a
[ISO8601](https://www.iso.org/iso-8601-date-and-time-format.html) subset,
because: [RFC3339](https://www.rfc-editor.org/rfc/rfc3339.html) is freely
accessible and ISO8601 is a cluster fuck of backwards compatibility and absurd
formats. Cutting the fat down to a subset of format strings was a good
decision. I can only recommend [RFC 3339 vs ISO 8601 vs
HTML](https://ijmacd.github.io/rfc3339-iso8601/), the visualisation shows the
whole scale of cursedness ISO8601 and HTML bring to the world. Also,
technically RFC3339 defines ISO8601 durations while not going into further
detail on them anywhere, see [RFC3339 - Appendix A. ISO 8601 Collected
ABNF](https://www.rfc-editor.org/rfc/rfc3339.html#page-12).

Germany (the country I am from and pay taxes to), contributes 7.6% of the OECD
budget per anno, applying this to membership fees of [ISO's financial
performance](https://www.iso.org/annual-reports/2023) in 2023:

| Operating revenue                                     | 2023   |
| ----------------------------------------------------- | ------ |
| Membership fees                                       | 21 359 |
| Royalties received from members selling ISO standards | 14 949 |
| Revenue from members                                  | 36 308 |
| Revenue – net sales                                   | 6 620  |
| **Funded activities**                                 |        |
| Funds to support Capacity Building activities         | 2 620  |
| Funds to support ISO Strategy                         | 1 800  |
| Funded activities - revenue                           | 4 420  |
| **Total revenue**                                     | 47 348 |

We get a staggering \(21359 \cdot 0.076 = 1623.284\)kCHF, which is around
\(1,737,227.20\textrm{€}\) of taxpayers money I contribute to. As a german I
love standards and the idea behind ISO and
[DIN](https://en.wikipedia.org/wiki/Deutsches_Institut_f%C3%BCr_Normung)
(Germanys ISO member body). What I don't love is my taxes going to a
organisation that produces standards that aren't freely accessible for anyone,
not for library implementers, not for oss contributors and not even for the tax
payers financing said organisation. To add insult to inury, they fucking charge
[227€](https://www.dinmedia.de/en/standard/iso-8601-2/303815655) for the
current ISO8601 version: _ISO 8601-2:2019-02_. Even the one before that costs
80 bucks. Anyway, I used the very good wikipedia [ISO8601 -
Durations](https://en.wikipedia.org/wiki/ISO_8601#Durations) and found some
public versions of the full spec ([ISO8601 - 4.4.3
Duration](https://www.loc.gov/standards/datetime/iso-tc154-wg5_n0038_iso_wd_8601-1_2016-02-16.pdf)),
out of all places, from the us library of congress .

# Understanding the Specification

_4.4.1 Separators and designators_ requires: "_[...] P shall precede [...] the
remainder of the [...] duration_".

_4.4.3.1 General_ defines a Duration as "_[...] a combination of components
with accurate duration (hour, minute and second) and components with nominal
duration (year, month, week and day)._". A component is made up of a variable
amount of numeric characters and a designator.

_4.4.3.2 Format with designators_ defines this further: "_The number of years
shall be followed by [...] Y_", "_the number of months by M_", "_the number of
weeks by W_", "_and the number of days by D_". "_[...] [the] time components
shall be preceded by [...] T_". It also defines "_[...] number of hours [...]
by H_", "_[...] minutes by M_" and "_[...] seconds by S_".

Furthermore "_[...] both basic and extended format [...] shall be PnnW or
PnnYnnMnnDTnnHnnMnnS_". The count of numeric characters (_nn_) before a
designator is somehow agreed upon by the members of the information exchange,
so even something absurd like 256 would be valid, who even thought that would
be smart? There are also some exceptions to the before:

1. "_[...] components may be omitted [...]_"
2. "_if necessary for a particular application, the lowest order components may
   have a decimal fraction_" (I skipped this one, because I don't think this is
   a good feature, but I'm open to adding this in the future, if necessary)
3. "_[...][if no other component is present] at least one number and its
   designator shall be present_"
4. "_[...] T shall be absent if all time components are absent_"

## Summary

1. A duration format string must start with a `P` for period
2. There are the following designators for the date component:
   - Y: year
   - M: month
   - D: day
3. There are the following designators for the time component:
   - H: hour
   - M: minute
   - S: second
4. Each designator needs a number and each number needs a designator
5. Pairs can be omitted, if empty
6. The time component must start with `T`, but can be omitted if no time
   designators are found
7. Using `W` is exclusive to all other designators
8. There always needs to be at least one designator and number pair

And some examples for the above:

| Example          | Pair wise               |
| ---------------- | ----------------------- |
| `P1Y2M3DT1H2M3S` | `P 1Y 2M 3D T 1H 2M 3S` |
| `P1Y2M3D`        | `P 1Y 2M 3D`            |
| `PT1H2M3S`       | `P T 1H 2M 3S`          |
| `P56W`           | `P 56W`                 |
| `P0D`            | `P 0D`                  |

# Handrolling ISO8601 Durations

After having somewhat understood the spec, lets get started with going through
my process of implementing the library.

## Defining a Duration Container

```go
type ISO8601Duration struct {
	year, month, week, day, hour, minute, second float64
}
```

## The API

A simple interaction interface:

```go
// P[nn]Y[nn]M[nn]DT[nn]H[nn]M[nn]S or P[nn]W, as seen in
// https://en.wikipedia.org/wiki/ISO_8601#Durations
//
// - P is the duration designator (for period) placed at the start of the duration representation.
//   - Y is the year designator that follows the value for the number of calendar years.
//   - M is the month designator that follows the value for the number of calendar months.
//   - W is the week designator that follows the value for the number of weeks.
//   - D is the day designator that follows the value for the number of calendar days.
//
// - T is the time designator that precedes the time components of the representation.
//   - H is the hour designator that follows the value for the number of hours.
//   - M is the minute designator that follows the value for the number of minutes.
//   - S is the second designator that follows the value for the number of seconds.
func From(s string) (ISO8601Duration, error) {}
func (i ISO8601Duration) Apply(t time.Time) time.Time {}
func (i ISO8601Duration) Duration() time.Duration {}
```

Using it as below:

```go
package main

import (
	"fmt"
	"time"

    "github.com/xnacly/go-iso8601-duration"
)

func main() {
	rawDuration := "PT1H30M12S"
	duration, err := goiso8601duration.From(rawDuration)
	if err != nil {
		panic(err)
	}

    // 1h30m12s PT1H30M12S
	fmt.Println(duration.Duration().String(), duration.String())
    // 01:00:00 02:30:12
	fmt.Println(
		time.
			Unix(0, 0).
			Format(time.TimeOnly),
		duration.
			Apply(time.Unix(0, 0)).
			Format(time.TimeOnly),
	)
}
```

I'm using this in production to interact with hafas data and so far I'm pretty
happy with it.

## Writing a Finite State Machine

The basis of any state machine, finite or not, is to define states the machine
should operate on. For a more theoretical deep dive, do read the [wikipedia
article](https://en.wikipedia.org/wiki/Finite-state_machine) on finite state
machines, its really good.

In general, the set of states is often defined by the differing input
components a format can have. Each state machine should have a start and an end
state. This makes bookkeeping for setting up internal state in the fsm easier
to reason about.

### Statify ISO8601

In the ISO8601 duration case, we of course also have the starting character,
`P`, which is required. The other atypical character, is the optional `T` which
instructs the parser to switch to _time_ mode.

After these initial states and the atypical states, we can go over to the pairs
of number and designator the duration format uses. We have to differentiate
between designators and numbers while in time and default mode, for this we use
`stateTNumber` and `stateTDesignator` in contrast to `stateNumber` and
`stateDesignator`:

```go
type state = uint8

const (
	stateStart state = iota
	stateP

	stateNumber
	stateDesignator

	stateT
	stateTNumber
	stateTDesignator

	stateFin
)
```

Since I like to have a mathematical definition for things like these, we can
pull up our mathematical fsm model. Its basically a quintuple of:

1. \(\Sigma\): Input alphabet:

   $$
   \{ P, T, Y, M, W, D, H, S, 0..9 \}
   $$

2. \(S\): finite non-empty set of states:

   $$
   \{ start, P, Number, Designator, T, TNumber, TDesignator, fin \}
   $$

3. \(s_0\): initial state, \(s_0 \in S\):

   $$
   start
   $$

4. \(\delta\): state transition function, which maps any state to its following state

   $$
   \delta := S \times \Sigma \rightarrow S
   $$

   However, since we need to be able to reject inputs, see [Dealing with
   unexpected state transitions](#dealing-with-unexpected-state-transitions),
   we can redefine \(\delta\) into a partial function as follows:

   $$
   \begin{align}
       \delta(s, x) &:= S \times \Sigma  \rightarrow S \\
       &\Leftrightarrow
       \begin{cases}
            P & \quad x = P, s = start \\
            T & \quad x = T, s \in \{P, Y, M, D, Designator\} \\
            Number & \quad x \in \{0..9\}, s \in \{P, Y, M, D, Designator\} \\
            Designator & \quad x \in \{Y,M,D,W\}, s \in \{Number\} \\
            TNumber & \quad x \in \{0..9\}, s \in \{T,TDesignator\} \\
            TDesignator & \quad x \in \{H,M,S\}, s \in \{TNumber\} \\
            fin & \quad \text{otherwise}
       \end{cases}
   \end{align}
   $$

5. \(F\): the final set of states:

   $$
   \{ fin \}
   $$

### State transitions

![state diagram for format](/handrolling-iso8601/chart.png)

### Stepping through ISO8601

Lets take for instance `P25W` and step through the fsm for this example:

| \(s\)        | \(x\) | \(\delta(s,x) \Rightarrow s_0\) | Input  |
| ------------ | ----- | ------------------------------- | ------ |
| `start`      | `P`   | `P`                             | `P25W` |
| `P`          | `2`   | `Number`                        | `25W`  |
| `Number`     | `5`   | `Number`                        | `5W`   |
| `Number`     | `W`   | `Designator`                    | `W`    |
| `Designator` | `EOF` | `fin`                           | ` `    |

The same applies for formats including time components, like `PT2M3S`

| \(s\)         | \(x\) | \(\delta(s,x) \Rightarrow s_0\) | Input    |
| ------------- | ----- | ------------------------------- | -------- |
| `start`       | `P`   | `P`                             | `PT2M3S` |
| `P`           | `T`   | `T`                             | `T2M3S`  |
| `T`           | `2`   | `TNumber`                       | `2M3S`   |
| `TNumber`     | `M`   | `TDesignator`                   | `M3S`    |
| `TDesignator` | `3`   | `TNumber`                       | `3S`     |
| `TNumber`     | `S`   | `TDesignator`                   | `S`      |
| `TDesignator` | `EOF` | `fin`                           | ` `      |

### Dealing with unexpected state transitions

Since I want to provide myself very extensive error contexts and I was
disappointed with the usual `unexpected input` shenanigans, I whipped up the
following error constants and the `ISO8601DurationError` for wrapping it with
the position the error occured in:

```go
package goiso8601duration

import (
	"errors"
	"fmt"
)

var (
	UnexpectedEof                  = errors.New("Unexpected EOF in duration format string")
	UnexpectedReaderError          = errors.New("Failed to retrieve next byte of duration format string")
	UnexpectedNonAsciiRune         = errors.New("Unexpected non ascii component in duration format string")
	MissingDesignator              = errors.New("Missing unit designator")
	UnknownDesignator              = errors.New("Unknown designator, expected YMWD or after a T, HMS")
	DuplicateDesignator            = errors.New("Duplicate designator")
	MissingNumber                  = errors.New("Missing number specifier before unit designator")
	TooManyNumbersForDesignator    = errors.New("Only 2 numbers before any designator allowed")
	MissingPDesignatorAtStart      = errors.New("Missing [P] designator at the start of the duration format string")
	NoDesignatorsAfterWeeksAllowed = errors.New("After [W] designator, no other numbers and designators are allowed")
)

type ISO8601DurationError struct {
	Inner  error
	Column uint8
}

func wrapErr(inner error, col uint8) error {
	return ISO8601DurationError{
		Inner:  inner,
		Column: col,
	}
}

func (i ISO8601DurationError) String() string {
	return fmt.Sprint("ISO8601DurationError: ", i.Inner, ", at col: ", i.Column)
}

func (i ISO8601DurationError) Error() string {
	return i.String()
}
```

These errors already hint at all the errors the fsm can encounter, lets go top
to bottom and contextualize each:

1. `UnexpectedEof`: not much to say here, the duration string ended
   unexpectedly
2. `UnexpectedReaderError`: reading a new rune from the input failed
3. `UnexpectedNonAsciiRune`: a read rune wasn't ascii, which a ISO8601 duration
   solely consists of
4. `MissingDesignator`: the fsm encountered a number but no matching
   designator, for instance something like `P5` instead of `P5D`
5. `UnknownDesignator`: the fsm found a designator it doesn't understand, only
   `YMWD` are valid in general and only `HMS` after `T`, `P12A` would be
   invalid, while `PT5D`, in place of `P5D` would be too
6. `DuplicateDesignator`: the fsm already set that designator, ISO8601 doesn't
   allow for duplicate duration unit designators, like `P2D10D`, which should
   be `P12D`
7. `MissingNumber`: the fsm encountered a designator before its number, for
   instance: `PD` instead of `P5D`
8. `TooManyNumbersForDesignator`: ISO8601 defines the amount of digit
   characters constructing the number before a designator to be decided by the
   producing and consuming party. Currently I used the examplary value of 2,
   which the spec uses and I found hafas to be using. Setting a unit number
   with more than two digit characters produces this error, for instance in
   `PT120S`.
9. `MissingPDesignatorAtStart`: ISO8601 requires all duration strings to start
   with `P` (short for `Period`), thus making all strings not conforming to
   this invalid inputs, this error reflects that. `12D` and `T5H` are invalid.
10. `NoDesignatorsAfterWeeksAllowed`: A duration including weeks (`W`) is
    exclusive to all other designators and designator values, making `P2W5D`
    and `P5D1W` invalid inputs.

For instance, in the part of the state machine that handles getting a new
character for advancing the state has several possible causes for failure, as
lined out before:

```go
func From(s string) (ISO8601Duration, error) {
	var duration ISO8601Duration

	if len(s) == 0 {
		return duration, wrapErr(UnexpectedEof, 0)
	}

	curState := stateStart
	var col uint8

	r := strings.NewReader(s)

	for {
		b, size, err := r.ReadRune()
		if err != nil {
			if err != io.EOF {
				return duration, wrapErr(UnexpectedReaderError, col)
			} else if curState == stateP {
				// being in stateP at the end (io.EOF) means we havent
				// encountered anything after the P, so there were no numbers
				// or states
				return duration, wrapErr(UnexpectedEof, col)
			} else if curState == stateNumber || curState == stateTNumber {
				// if we are in the state of Number or TNumber we had a number
				// but no designator at the end
				return duration, wrapErr(MissingDesignator, col)
			} else {
				curState = stateFin
			}
		}
		if size > 1 {
			return duration, wrapErr(UnexpectedNonAsciiRune, col)
		}
		col++

        // ...
	}
}
```

Another case for failure is of course the `start->P` transition, which is
mandatory for any valid input:

```go
func From(s string) (ISO8601Duration, error) {
    // ...
	for {
        // ...
		switch curState {
		case stateStart:
			if b != 'P' {
				return duration, wrapErr(MissingPDesignatorAtStart, col)
			}
			curState = stateP
        // ...
	}
}
```

### Parsing numbers

As I explained above, I went for a maximum of two digit characters to make up
the designator value:

```go
// This parser uses the examplary notion of allowing two numbers before any
// designator, see: ISO8601 4.4.3.2 Format with designators
const maxNumCount = 2
```

This is reflected in the temporary buffer the fsm uses to store the digit
characters as it walks the input:

```go
var curNumCount uint8
var numBuf [maxNumCount]rune
```

When encountering an integer it puts this integer into the buffer:

```go
case stateTNumber:
    if unicode.IsDigit(b) {
        if curNumCount+1 > maxNumCount {
            return duration, wrapErr(TooManyNumbersForDesignator, col)
        }
        numBuf[curNumCount] = b
        curNumCount++
        curState = stateTNumber
    }
    // ...
```

If it hits a designator, either in the context of time (`T`) or not, it uses
this rune buffer to produce an integer to assign to the corresponding field of
the `ISO8601Duration` struct:

```go
const defaultDesignators = "YMWD"
const timeDesignators = "MHS"

case stateTNumber:
    // ...
    if strings.ContainsRune(timeDesignators, b) {
        if curNumCount == 0 {
            return duration, wrapErr(MissingNumber, col)
        }
        num := numBufferToNumber(numBuf)
        switch b {
        case 'H':
            if duration.hour != 0 {
                return duration, wrapErr(DuplicateDesignator, col)
            }
            duration.hour = float64(num)
        case 'M':
            if duration.minute != 0 {
                return duration, wrapErr(DuplicateDesignator, col)
            }
            duration.minute = float64(num)
        case 'S':
            if duration.second != 0 {
                return duration, wrapErr(DuplicateDesignator, col)
            }
            duration.second = float64(num)
        }
        curNumCount = 0
        numBuf = [maxNumCount]rune{}
        curState = stateTDesignator
    } else {
        return duration, wrapErr(UnknownDesignator, col)
    }
```

`numBufferToNumber` is as simple as number conversion gets:

```go
func numBufferToNumber(buf [maxNumCount]rune) int64 {
	var i int
	for _, n := range buf {
		if n == 0 { // empty number (zero byte) in buffer, stop
			break
		}
		i = (i * 10) + int(n-'0')
	}

	return int64(i)
}
```

I chose this way to omit the allocation of a string and the call to
`strconv.ParseInt` by doing the work myself.

### The whole machine

```go
func From(s string) (ISO8601Duration, error) {
	var duration ISO8601Duration

	if len(s) == 0 {
		return duration, wrapErr(UnexpectedEof, 0)
	}

	curState := stateStart
	var col uint8
	var curNumCount uint8
	var numBuf [maxNumCount]rune

	r := strings.NewReader(s)

	for {
		b, size, err := r.ReadRune()
		if err != nil {
			if err != io.EOF {
				return duration, wrapErr(UnexpectedReaderError, col)
			} else if curState == stateP {
				// being in stateP at the end (io.EOF) means we havent
				// encountered anything after the P, so there were no numbers
				// or states
				return duration, wrapErr(UnexpectedEof, col)
			} else if curState == stateNumber || curState == stateTNumber {
				// if we are in the state of Number or TNumber we had a number
				// but no designator at the end
				return duration, wrapErr(MissingDesignator, col)
			} else {
				curState = stateFin
			}
		}
		if size > 1 {
			return duration, wrapErr(UnexpectedNonAsciiRune, col)
		}
		col++

		switch curState {
		case stateStart:
			if b != 'P' {
				return duration, wrapErr(MissingPDesignatorAtStart, col)
			}
			curState = stateP
		case stateP, stateDesignator:
			if b == 'T' {
				curState = stateT
			} else if unicode.IsDigit(b) {
				if curNumCount > maxNumCount {
					return duration, wrapErr(TooManyNumbersForDesignator, col)
				}
				numBuf[curNumCount] = b
				curNumCount++
				curState = stateNumber
			} else {
				return duration, wrapErr(MissingNumber, col)
			}
		case stateNumber:
			if unicode.IsDigit(b) {
				if curNumCount+1 > maxNumCount {
					return duration, wrapErr(TooManyNumbersForDesignator, col)
				}
				numBuf[curNumCount] = b
				curNumCount++
				curState = stateNumber
			} else if strings.ContainsRune(defaultDesignators, b) {
				if curNumCount == 0 {
					return duration, wrapErr(MissingNumber, col)
				}
				num := numBufferToNumber(numBuf)
				switch b {
				case 'Y':
					if duration.year != 0 {
						return duration, wrapErr(DuplicateDesignator, col)
					}
					duration.year = float64(num)
				case 'M':
					if duration.month != 0 {
						return duration, wrapErr(DuplicateDesignator, col)
					}
					duration.month = float64(num)
				case 'W':
					if r.Len() != 0 {
						return duration, wrapErr(NoDesignatorsAfterWeeksAllowed, col)
					}
					duration.week = float64(num)
				case 'D':
					if duration.day != 0 {
						return duration, wrapErr(DuplicateDesignator, col)
					}
					duration.day = float64(num)
				}
				curNumCount = 0
				numBuf = [maxNumCount]rune{}
				curState = stateDesignator
			} else {
				return duration, wrapErr(UnknownDesignator, col)
			}
		case stateT, stateTDesignator:
			if unicode.IsDigit(b) {
				if curNumCount > maxNumCount {
					return duration, wrapErr(TooManyNumbersForDesignator, col)
				}
				numBuf[curNumCount] = b
				curNumCount++
				curState = stateTNumber
			} else {
				return duration, wrapErr(MissingNumber, col)
			}
		case stateTNumber:
			if unicode.IsDigit(b) {
				if curNumCount+1 > maxNumCount {
					return duration, wrapErr(TooManyNumbersForDesignator, col)
				}
				numBuf[curNumCount] = b
				curNumCount++
				curState = stateTNumber
			} else if strings.ContainsRune(timeDesignators, b) {
				if curNumCount == 0 {
					return duration, wrapErr(MissingNumber, col)
				}
				num := numBufferToNumber(numBuf)
				switch b {
				case 'H':
					if duration.hour != 0 {
						return duration, wrapErr(DuplicateDesignator, col)
					}
					duration.hour = float64(num)
				case 'M':
					if duration.minute != 0 {
						return duration, wrapErr(DuplicateDesignator, col)
					}
					duration.minute = float64(num)
				case 'S':
					if duration.second != 0 {
						return duration, wrapErr(DuplicateDesignator, col)
					}
					duration.second = float64(num)
				}
				curNumCount = 0
				numBuf = [maxNumCount]rune{}
				curState = stateTDesignator
			} else {
				return duration, wrapErr(UnknownDesignator, col)
			}
		case stateFin:
			return duration, nil
		}
	}
}
```

## Go time Compatibility

Since the whole usecase for this library is to interact with the go `time`
package, it needs conversion to do exactly that.

### Apply

As the name suggests this function takes a `time.Time`, applies the value
encoded in `ISO8601Duration` to it and returns a resulting `time.Time`
instance.

```go
func (i ISO8601Duration) Apply(t time.Time) time.Time {
	newT := t.AddDate(int(i.year), int(i.month), int(i.day+i.week*7))
	d := time.Duration(
		(i.hour * float64(time.Hour)) +
			(i.minute * float64(time.Minute)) +
			(i.second * float64(time.Second)),
	)
	return newT.Add(d)
}
```

### Duration

Duration is a bit more complicated. I had to approximate some values (like
`daysPerYear` and `daysPerMonth`) which of course doesn't account for the
whole lap year/lap day fuckery.

```go
func (i ISO8601Duration) Duration() time.Duration {
	const (
		nsPerSecond  = int64(time.Second)
		nsPerMinute  = int64(time.Minute)
		nsPerHour    = int64(time.Hour)
		nsPerDay     = int64(24 * time.Hour)
		nsPerWeek    = int64(7 * 24 * time.Hour)
		daysPerYear  = 365.2425
		daysPerMonth = 30.436875
	)

	var ns int64

	ns += int64(i.year * daysPerYear * float64(nsPerDay))
	ns += int64(i.month * daysPerMonth * float64(nsPerDay))
	ns += int64(i.week * float64(nsPerWeek))
	ns += int64(i.day * float64(nsPerDay))
	ns += int64(i.hour * float64(nsPerHour))
	ns += int64(i.minute * float64(nsPerMinute))
	ns += int64(i.second * float64(nsPerSecond))

	return time.Duration(ns)
}
```

## Serializing via the Stringer interface

```go
// Stringer is implemented by any value that has a String method,
// which defines the “native” format for that value.
// The String method is used to print values passed as an operand
// to any format that accepts a string or to an unformatted printer
// such as [Print].
type Stringer interface {
	String() string
}
```

Implementing this is fairly easy: at a high level: It consists of checking for
each field whether its 0, if not write the value (`nn`) and its designator
(`YMDHMS`). Edgecases are:

- all fields are zero -> write `P0D`
- time fields are set, prefix with `T`
- field `week` is non zero -> write only the week `PnnW`, nothing else

```go
func (i ISO8601Duration) String() string {
	b := strings.Builder{}
	b.WriteRune('P')

	// If the number of years, months, days, hours, minutes or seconds in any of these expressions equals
	// zero, the number and the corresponding designator may be absent; however, at least one number
	// and its designator shall be present
	if i.year == 0 && i.month == 0 && i.week == 0 && i.day == 0 && i.hour == 0 && i.minute == 0 && i.second == 0 {
		b.WriteString("0D")
		return b.String()
	}

	if i.week > 0 {
		b.WriteString(strconv.FormatFloat(i.week, 'g', -1, 64))
		b.WriteRune('W')
		return b.String()
	}

	if i.year > 0 {
		b.WriteString(strconv.FormatFloat(i.year, 'g', -1, 64))
		b.WriteRune('Y')
	}
	if i.month > 0 {
		b.WriteString(strconv.FormatFloat(i.month, 'g', -1, 64))
		b.WriteRune('M')
	}
	if i.day > 0 {
		b.WriteString(strconv.FormatFloat(i.day, 'g', -1, 64))
		b.WriteRune('D')
	}

	// The designator [T] shall be absent if all of the time components are absent.
	if i.hour > 0 || i.minute > 0 || i.second > 0 {
		b.WriteRune('T')

		if i.hour > 0 {
			b.WriteString(strconv.FormatFloat(i.hour, 'g', -1, 64))
			b.WriteRune('H')
		}

		if i.minute > 0 {
			b.WriteString(strconv.FormatFloat(i.minute, 'g', -1, 64))
			b.WriteRune('M')
		}

		if i.second > 0 {
			b.WriteString(strconv.FormatFloat(i.second, 'g', -1, 64))
			b.WriteRune('S')
		}
	}

	return b.String()
}
```

## Extensive testing

Since most of my critisism of the existing libraries were either no spec
compliance and or accepting weird inputs I made sure to do extensive testing
before publishing the library.

### Edgecases

Some of these are inputs I tried throwing at other libraries to test their
compliance and how in depth their error messages are.

```go
// TestDurationErr makes sure all expected edgecases are implemented correctly
func TestDurationErr(t *testing.T) {
	cases := []string{
		"",        // UnexpectedEof
		"P",       // UnexpectedEof
		"è",       // UnexpectedNonAsciiRune
		"P1",      // MissingDesignator
		"P1A",     // UnknownDesignator
		"P12D12D", // DuplicateDesignator
		"P1YD",    // MissingNumber
		"P111Y",   // TooManyNumbersForDesignator
		"Z",       // MissingPDesignatorAtStart
		"P15W2D",  // NoDesignatorsAfterWeeksAllowed
	}

	for _, i := range cases {
		t.Run(i, func(t *testing.T) {
			_, err := From(i)
			if assert.Error(t, err) {
				fmt.Println(err)
			}
		})
	}
}
```

{{<shellout>}}
$ go test ./... -v
%SEPARATOR%
=== RUN TestDurationErr
=== RUN TestDurationErr/#00
ISO8601DurationError: Unexpected EOF in duration format string, at col: 0
=== RUN TestDurationErr/P
ISO8601DurationError: Unexpected EOF in duration format string, at col: 1
=== RUN TestDurationErr/è
ISO8601DurationError: Unexpected non ascii component in duration format string, at col: 0
=== RUN TestDurationErr/P1
ISO8601DurationError: Missing unit designator, at col: 2
=== RUN TestDurationErr/P1A
ISO8601DurationError: Unknown designator, expected YMWD or after a T, HMS, at col: 3
=== RUN TestDurationErr/P12D12D
ISO8601DurationError: Duplicate designator, at col: 7
=== RUN TestDurationErr/P1YD
ISO8601DurationError: Missing number specifier before unit designator, at col: 4
=== RUN TestDurationErr/P111Y
ISO8601DurationError: Only 2 numbers before any designator allowed, at col: 4
=== RUN TestDurationErr/Z
ISO8601DurationError: Missing [P] designator at the start of the duration format string, at col: 1
=== RUN TestDurationErr/P15W2D
ISO8601DurationError: After [W] designator, no other numbers and designators are allowed, at col: 4
{{</shellout>}}

### Happy paths

Each testcase crafted so I hit all branches and possibilites the spec defines.

```go
var testcases = []struct {
	str string
	dur ISO8601Duration
}{
	{"P0D", ISO8601Duration{}},
	{"PT15H", ISO8601Duration{hour: 15}},
	{"P1W", ISO8601Duration{week: 1}},
	{"P15W", ISO8601Duration{week: 15}},
	{"P15Y", ISO8601Duration{year: 15}},
	{"P15Y3M", ISO8601Duration{year: 15, month: 3}},
	{"P15Y3M41D", ISO8601Duration{year: 15, month: 3, day: 41}},
	{"PT15M", ISO8601Duration{minute: 15}},
	{"PT15M10S", ISO8601Duration{minute: 15, second: 10}},
	{
		"P3Y6M4DT12H30M5S",
		ISO8601Duration{
			year:   3,
			month:  6,
			day:    4,
			hour:   12,
			minute: 30,
			second: 5,
		},
	},
}

func TestDurationStringer(t *testing.T) {
	for _, i := range testcases {
		t.Run(i.str, func(t *testing.T) {
			stringified := i.dur.String()
			assert.Equal(t, i.str, stringified)
		})
	}
}

func TestDuration(t *testing.T) {
	for _, i := range testcases {
		t.Run(i.str, func(t *testing.T) {
			parsed, err := From(i.str)
			assert.NoError(t, err)
			assert.Equal(t, i.dur, parsed)
		})
	}
}

func TestBiliteral(t *testing.T) {
	for _, i := range testcases {
		t.Run(i.str, func(t *testing.T) {
			parsed, err := From(i.str)
			assert.NoError(t, err)
			assert.Equal(t, i.dur, parsed)
			stringified := parsed.String()
			assert.Equal(t, i.str, stringified)
		})
	}
}
```
