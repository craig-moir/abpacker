commit:
	git commit -a 

push:
	make commit
	git push

simple_commit:
	git commit -a -m"more work"

simple_push:
	make simple_commit
	git push
