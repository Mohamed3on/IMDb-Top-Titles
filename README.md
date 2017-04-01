# IMDb Top Titles
This is a script to find the best titles on IMDb, based on a score that is (number of likes - number of dislikes).
### What are likes/dislikes?
Likes are the number of people who gave the title a 10 or a 9 rating, which is the same as 4.5-5/5 ratings, which for me is a great way to tell that person really liked that title. 

In a similar fashion, dislikes are the number of 1 and 2 ratings, which translate to 0.5-1/5, which are the number of people who *really* disliked that title.

The rest of the votes (3-8) are, for me, not as important. I don't care about a movie that most people gave a 7 rating, these ratings pretty much translate to 'meh', and 'meh' votes are irrelevant.
### Why likes - dislikes?
Because I want to know what titles are:
1. popular (have many votes).
2. are liked by many of who saw it.
3. are disliked by few of who saw it.
### How to use it?
You can just run the movies.py script if you want a list of the best titles voted by 25000 or more. you can change the number of minimum votes, or the url of the list, provided the url looks like this format: [IMDb](http://imdb.com/search/title?count=250&num_votes=25000,&sort=num_votes,desc&view=simple).
## Just IMDb titles?
No, I also made a similar script for bookreads books, this time likes are 5 ratings, and dislikes are 1 ratings. It works in a similar fashion, by parsing the 50 most read books this year, and making an alternative list out of it. You can also give it any other page to parse, for example:  [A list of 50 popular programming books](https://www.goodreads.com/shelf/show/programming).
##Questions?
Please submit an issue if you have any inquiry!
