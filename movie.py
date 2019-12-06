class Movie:

    def __init__(self,imdbId, original_title, title,genres, duration, release_date, rating, imdbScore):
        self.imdbId = imdbId
        self.original_title = original_title
        self.title = title
        self.duration = duration
        self.release_date = release_date
        self.genres = genres
        self.imdbScore = imdbScore

        self.rating = None
        self.id = None
        self.actors = []
        self.productors = []
        self.is_3d = None
        self.production_budget = None
        self.marketing_budget = None
        self.synopsis = None

        self.boxOffice = None
        

    def total_budget(self):
        if (self.production_budget == None or self.marketing_budget == None):
            return None
        
        return self.production_budget + self.marketing_budget