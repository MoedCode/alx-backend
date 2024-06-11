#!/usr/bin/env node
const Express = require('express');
const Redis = require('redis');
const fs = require('fs');

Redis.toString = function () {
    let strObj = ""; // Initialize an empty string to build the representation

    // Define the convert function to process the object
    const convert = (obj, nest = false) => {
        if (nest) strObj += "    "; // Add indentation if nested
        strObj += "{\n"; // Start the object representation

        // Iterate over all keys in the object
        for (let key in obj) {
            // Check if the property is its own and not inherited
            if (obj.hasOwnProperty(key)) {
                if (typeof obj[key] === 'function') {
                    // If the value is a function, handle it accordingly
                    strObj += `   " ${key} " : "function ${obj[key].name}() {...}"\n`;
                } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                    // If the value is an object, recursively convert it
                    strObj += `   " ${key} " : `;
                    convert(obj[key], true);
                    strObj += '\n';
                } else {
                    // Otherwise, add the key-value pair to the string
                    strObj += `   " ${key} " : "${obj[key]}"\n`;
                }
            }
        }
        strObj += "}"; // Close the object representation
    }

    convert(this); // Call the convert function with 'this' referring to the Redis object
    return strObj; // Return the final string representation
}

// Print the string representation of the Redis object
console.log(Redis.toString());
