// logToSheets.js
const express = require("express");
const fetch = require("node-fetch");

const router = express.Router();

// Replace with your actual deployed Google Apps Script URL
const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzrpW3Vj_Xz2UTsvlyI4B9fe1d3uIvMry5FI9DIUhTJfQFErVYxY659VYCBzu0xwh8i/exec";

router.post("/log-to-sheets", async (req, res) => {
  try {
    const payload = JSON.stringify(req.body);

    const googleResponse = await fetch(GOOGLE_SCRIPT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload,
    });

    const text = await googleResponse.text();
    res.status(200).send(text);
  } catch (error) {
    console.error("Proxy error:", error);
    res.status(500).json({ error: "Proxy failed", detail: error.message });
  }
});

module.exports = router;
