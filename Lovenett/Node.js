const express = require('express');
const multer = require('multer');
const app = express();

const upload = multer({ dest: 'uploads/' });

app.post('/upload-audio', upload.single('audio'), (req, res) => {
    console.log("Fichier reçu :", req.file);
    res.json({ url: `/audios/${req.file.filename}` });
});

app.listen(3000);