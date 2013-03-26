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
		.description 
		{
			color: grey;
			display: inline;
        }      
        dt
        { 
			cursor: hand; cursor: pointer; 
		}
		.left
		{
			width: 120px;			
			float: left;
		}
		.right
		{
			max-width: 600px;
			width: 100%;				
			float: left;
		}
				
	</style>
</head>
<body>
	<dl class = "left">
		%for channel in channels:
		<dt class = "channel">				
		<a href = "/{{channel['url']}}">
			<h2 class="title">{{channel['title']}}</h2> 
		</a>					
		</dt>		
		%end	
	</dl>
	<dl class = "accordion right">
		%for item in items:
		<dt class = "item">				
			<h2 class="title">{{item['title']}}</title> -
			<span class="description">
				{{item['description']}}
			</span>			
		</dt>
		<dd>
			{{item['description']}}
		</dd>
		%end	
	</dl>
</body>

</html>
<script>
	$('.accordion dd').hide();
	$('.accordion dt').click(function(){
    cur_stus = $(this).attr('stus');
    if(cur_stus != "active")
    {
        //reset everthing - content and attribute
        $('.accordion dd').slideUp();
        $('.accordion dt').attr('stus', '');
 
        //then open the clicked data
        $(this).next().slideDown();
        $(this).attr('stus', 'active');
    }
    return false;
	});
</script>
