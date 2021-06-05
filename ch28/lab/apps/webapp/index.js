// SSRF

const http = require('http');
const needle = require('needle');
const express = require('express');
const app = express();
const port = 8080

app.get('/', function(req, res) {
    var params = req.params;
    var url = req.query['url'];
    if (req.query['mime'] == 'plain'){
	var mime = 'plain';
    } else {
	var mime = 'html';
    };

    if (url == undefined) {
        res.write('<p>Please make sure to pass url into the request. Example: www.test.com/?url=www.test.com</p>');
    } else {

    needle.get(url, { timeout: 3000 }, function(error, res1) {
      if (!error && res1.statusCode == 200) {
        res.writeHead(200, {'Content-Type': 'text/'+mime});
        res.write('<h1>This app has an SSRF\n</h1>');
        res.write('<h2>Requested URL: '+url+'\n</h2><br><br>\n<pre>');
        res.write(res1.body);
        res.write('</pre>');
        res.end();
      } else {
        res.writeHead(404, {'Content-Type': 'text/'+mime});
        res.write('<h1>This app has an SSRF\n</h1>');
        res.write('<h2>Cant find this URL: '+url+'\n</h2><br><br>\n');
        res.end();

      }
    });
   }
})

app.listen(port);
console.log('|  Server listening for connections on port:'+port);
console.log('|  Connect to server using the following url: \n|  -- http://[server]:'+port+'/?url=[SSRF URL]');
console.log('|\n`------------------------------------------------');
