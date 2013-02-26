(function($) {
  // NOTE: No atributes are added to class. They can be added dynamically.
  window.Score = Backbone.Model.extend({
      initialize: function() {
      },

      validate: function(attributes) {
        return !!attributes.foodType || !! attributes.date  ? false : true;
      },
  });

  window.Scores = Backbone.Collection.extend({
    model: Score,
    url: '/scores',
  });

  window.scores = new Scores();

  $(document).ready(function() {
    window.ScoreView = Backbone.View.extend({
      tagName: 'li',
      className: 'score-view',
      template: _.template($('#score-template').html()),

      render: function() {
        var renderedContent = this.template(this.model.toJSON());
        this.$el.html(renderedContent);

        return this;
      }
    });

    window.ScoresView = Backbone.View.extend({
      tagName: 'section',
      template: _.template($('#scores-template').html()),

      initialize: function() {
        // "bind" and "on" are the same thing
        this.collection.on('reset', this.render, this);
        this.collection.on('add', this.addScore, this);
      },

      render: function() {
        this.$el.html(this.template());

        var self = this;
        this.collection.each(function(score) {
          var scoreView = new ScoreView({model: score});
          self.$('ol').append(scoreView.render().el);
        });
        
        return this;
      },

      addScore: function(model, collection, options) {
        var score = new Score({
          foodType: model.attributes.foodType,
          date: model.attributes.date,
          score: model.attributes.score
        });

        var scoreView = new ScoreView({
          model: score
        });

        this.$('ol').append(scoreView.render().el);
      },
    });

    window.TotalScoresView = Backbone.View.extend({
      tagName: 'section',
      template: _.template($('#total-score-template').html()),

      initialize: function() {
        this.collection.on('sync', this.render, this);
      },

      render: function(e) {
        var self = this;
        var scoreView;
        var renderedContent;
        var totalScore = this.collection.reduce(function(memo, score) {
          console.log(memo, score.attributes.score, memo+score.attributes.score);
          return memo + score.attributes.score;
        }, 0);

        renderedContent = this.template({totalScore: totalScore});
        this.$el.html(renderedContent);

        return this;
      },
    });

    window.NewFoodView = Backbone.View.extend({
      tagName: 'section',
      template: _.template($('#new-food-template').html()),
      events: {
        'keypress #new-food': 'saveOnEnter',
      },

      initialize: function() {
      },

      render: function(e) {
        $(this.el).html(this.template());
        return this
      },

      saveOnEnter: function(event) {
        if (event.keyCode == 13) {
          // TODO: read event.preventDefault docs.
          event.preventDefault();

          this.collection.create({
            foodType: $('#new-food').val(),
            date: parseInt(moment().format('YYYYMMDD'))
          }, {
            wait: true,
            validate: true,
          });
        }
      },
    });

    window.DQSRouter = Backbone.Router.extend({
      routes: {
        '': 'index',
      },

      initialize: function() {
        this.scoresView = new ScoresView({
          collection: scores,
        });

        this.newFoodView = new NewFoodView({
          collection: scores,
        });

        this.totalScoreView = new TotalScoresView({
          collection: scores,
        });
      },

      index: function() {
        $('#container').empty();
        $('#container').append(this.totalScoreView.render().el);
        $('#container').append(this.scoresView.render().el);
        $('#container').append(this.newFoodView.render().el);
      },
    });

    window.App = new DQSRouter();
    Backbone.history.start();
  });
  
  window.DQS = window.DQS || {};
  DQS.Scores = Backbone.Collection.extend({});

})(jQuery);
