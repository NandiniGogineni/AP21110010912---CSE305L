const mysql = require('mysql');

// Create a connection to the database
const connection = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'bug1',
  });

// Connect to the database
connection.connect();

// Query to retrieve table names
const query = "SHOW TABLES";

// Execute the query
connection.query(query, function (error, results, fields) {
  if (error) throw error;

  console.log('Tables in the database:');
  results.forEach(result => {
    console.log(result[fields[0].name]);
  });
});

// Close the connection
connection.end();
