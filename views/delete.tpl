%from bottle import url
Delete channel {{channel.title}}? 
<form action="{{url('/channels/<id:int>/delete', id=channel.id)}}" method="post">
<input type ="submit" value="Ok"></form>
</form>
