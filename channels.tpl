<html>
<head>
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>

	<style type="text/css">
		body
		{
			font-family: sans-serif;
			font-size: 0.9em;
			margin: 0;
			padding: 0;
		}
		.item
		{
			overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            margin-top: 0;
            margin-bottom: 0;
            padding-top: 0.4em;
            padding-bottom: 0.5em;
            padding-left: 0.5em;
            border-bottom: 1px solid grey;            
		}
		.title {				
			font-size: 100%;
			margin: 0;
			padding: 0;
			font-weight: bold;
			display: inline;						
		}		    
       
				
	</style>
</head>
<body>
	<dl class = "accordion">
		%for channel in channels:
		<dt class = "item">				
		<a href = "/{{channel['url']}}">
			<h2 class="title">{{channel['title']}}</h2> 
		</a>					
		</dt>		
		%end	
	</dl>
</body>

</html>

