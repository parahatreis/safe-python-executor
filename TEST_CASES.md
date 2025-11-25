# Test Cases

## 1. Happy Path: Simple Script

**Goal:** Verify successful execution, main() return value, and captured stdout.

**Request:**

```http
POST /execute
Content-Type: application/json
```

**Body:**

```json
{
  "script": "def main():\n    print('Hello from script')\n    return {\"status\": \"ok\", \"value\": 42}\n"
}
```

**Expected Response:**
- Status: 200
- Body structure:

```json
{
  "result": {
    "status": "ok",
    "value": 42
  },
  "stdout": "Hello from script\n"
}
```

---

## 2. Happy Path: Script Using NumPy or Pandas

**Goal:** Check that required libs are available and still serializable.

**Request:**

```http
POST /execute
Content-Type: application/json
```

**Body** (example using numpy, but keep result JSON friendly):

```json
{
  "script": "import numpy as np\n\ndef main():\n    arr = np.array([1, 2, 3])\n    print('Array:', arr)\n    return {\"sum\": int(arr.sum())}\n"
}
```

**Expected Response:**
- Status: 200
- Body structure:

```json
{
  "result": {
    "sum": 6
  },
  "stdout": "Array: [1 2 3]\n"
}
```

---

## 3. Validation: Non-JSON Request Body

**Goal:** Trigger InvalidContentType or InvalidJSON depending on how you handle it.

**Request:**

```http
POST /execute
Content-Type: text/plain
```

**Body:**

```
just some plain text, not json
```

**Expected Response:**
- Status: 400
- Body structure:

```json
{
  "error": {
    "type": "InvalidContentType",
    "message": "Request must be application/json"
  }
}
```

> Note: Or a similar message if you collapse it into a generic JSON error.

---

## 4. Validation: Missing Script Field

**Goal:** Ensure Pydantic (or your manual validation) catches missing required field.

**Request:**

```http
POST /execute
Content-Type: application/json
```

**Body:**

```json
{
  "code": "def main():\n    return 1\n"
}
```

**Expected Response:**
- Status: 400
- Body structure (example):

```json
{
  "error": {
    "type": "ValidationError",
    "message": "... 'script' field is required ..."
  }
}
```

> Note: The exact message can be whatever Pydantic generates or your custom text, but it should clearly indicate script is missing.

---

## 5. Script Error: Main Missing or Not Callable

**Goal:** Verify MissingMain mapping and that the service does not crash.

**Request:**

```http
POST /execute
Content-Type: application/json
```

**Body:**

```json
{
  "script": "def not_main():\n    print('I am not main')\n"
}
```

**Expected Response:**
- Status: 400
- Body structure:

```json
{
  "error": {
    "type": "MissingMain",
    "message": "Script must define a callable main() function"
  }
}
```
