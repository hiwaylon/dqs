(function($) {
  // NOTE: No atributes are added to class. They can be added dynamically.
  window.Score = Backbone.Model.extend({});

  window.ScoreView = Backbone.View.extend({
    initialize: function() {
      this.template = _.template($("#score-template").html());
    },

    render: function() {
      console.log(this.model.toJSON());
      var renderedContent = this.template(this.model.toJSON());
      $(this.el).html(renderedContent);
      return this;
    }
  });

  // COFFEE:
  //  class Score extends Backbone.Model
  //    ...
  //

})(jQuery);