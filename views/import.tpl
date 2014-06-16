%from bottle import url
<form action="{{url('/channels/import')}}" method="POST" enctype="multipart/form-data">
<ul>
<li>	
	<input type="file" name = "file" class="file" accept="text/xml"/>
</li>
<li>
	<input type="submit" value = "Import">
</li>
</ul>
</form>
