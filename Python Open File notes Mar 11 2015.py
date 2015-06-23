

# writing process
Step 1 dumpjson to dictionary
jsom.dumps(x)
Step 2 write dictionary to file
with open('test.csv', 'w') as csvfile:
	fieldnames = y.keys()
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	writer.writerow(y)

# reading process
with open('test.csv') as csvfile:
	count = 1
	reader = csv.DictReader(csvfile)
	for row in reader:
                print((json.dumps(row, indent=4)))


>>> payload = {'key1': 'value1', 'key2': 'value2'}
>>> r = requests.post("http://httpbin.org/post", data=payload)
>>> print(r.text)
{
  ...
  "form": {
    "key2": "value2",
    "key1": "value1"
  },
  ...
}
