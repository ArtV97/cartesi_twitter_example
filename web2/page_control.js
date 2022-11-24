// tweet array items
const id = 0
const user = 1
const msg = 2
const timestamp = 3
const likes = 4     // counter
const retweets = 5  // counter
const replies = 6   // counter


let tweets_count            // total tweets
let curr_tweets_count = 0   // total tweets displayed in interface feed


function post_tweet() {

}

function reply() {

}

function retweet() {

}

function like() {

}


function display_update_option() {
    let new_tweets = tweets_count - curr_tweets_count
    let update_tweets_elem = document.getElementById("update_tweets")

    update_tweets_elem.innerHTML = `
        <button type="submit" class="btn btn-outline-dark border-0 p-2" onclick="update_tweets()">
            Show new Tweets (${new_tweets})
        </button>
    `
}

function update_tweets() {
    let feed_elem = document.getElementById("feed")

    query_db([["get_tweets_feed"]], (res) => {
        let tweets = res[0]

        for (let i = tweets.length -1; i >= curr_tweets_count; i--) {
            feed_elem.innerHTML += `
                <li class="list-group-item"style="background-color: floralwhite;">
                <div class="row p-1">
                <img src="user.png" class="col-2 rounded-circle border", style="height: 75px; width: 75px;">
                <div class="col">
                <div>
                <span>${tweets[i][user]}</span>
                <i class="bi bi-dot m-1"></i>
                <span>${tweets[i][timestamp]}</span>
                </div>
                
                <div>
                <p>${tweets[i][msg]}</p>

                <button type="button" class="btn btn-outline-dark"><i class="bi bi-chat"></i> ${tweets[i][replies]}</button>
                <button type="button" class="btn btn-outline-dark mx-5"><i class="bi bi-arrow-repeat"></i> ${tweets[i][retweets]}</button>
                <button type="button" class="btn btn-outline-dark"><i class="bi bi-heart"> ${tweets[i][likes]}</i></button>
                
                </div>
                </div>
                </div>
                </li>
            `
        }
    
        tweets_count = tweets.length
        curr_tweets_count = tweets_count

        let update_tweets_elem = document.getElementById("update_tweets")
        update_tweets_elem.innerHTML = "" // clear
    })
}

update_tweets()

window.setInterval(() => {
    query_db([ ["count_tweets_feed"] ], (res) => {
        tweets_count = res[0]

        if (curr_tweets_count != tweets_count) {
            display_update_option()
        }

    })
}, 10000);